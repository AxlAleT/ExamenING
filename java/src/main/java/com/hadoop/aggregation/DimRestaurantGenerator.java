package com.hadoop.aggregation;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

/**
 * MapReduce job to generate the Restaurant dimension table
 */
public class DimRestaurantGenerator extends BaseDimensionGenerator {
    
    /**
     * Mapper class that reads from MySQL and emits restaurant dimension records
     */
    public static class RestaurantMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        private Connection connection;
        
        @Override
        protected void setup(Context context) throws IOException, InterruptedException {
            try {
                // Get database connection
                Class.forName(DBConfig.JDBC_DRIVER);
                connection = DriverManager.getConnection(DBConfig.DB_URL, DBConfig.DB_USER, DBConfig.DB_PASSWORD);
            } catch (Exception e) {
                throw new IOException("Could not connect to database", e);
            }
        }
        
        @Override
        protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            try {
                // Query to get restaurant data
                String query = "SELECT restaurant_id, restaurant_name, cuisine_type FROM restaurants";
                PreparedStatement stmt = connection.prepareStatement(query);
                ResultSet rs = stmt.executeQuery();
                
                // Generate restaurant dimension records
                // For the average rating, we'll calculate it from the orders table
                while (rs.next()) {
                    int restaurantId = rs.getInt("restaurant_id");
                    String restaurantName = rs.getString("restaurant_name");
                    String cuisineType = rs.getString("cuisine_type");
                    
                    // Get average rating for the restaurant
                    String ratingQuery = "SELECT AVG(rating) as avg_rating FROM orders WHERE restaurant_id = ? AND rating IS NOT NULL";
                    PreparedStatement ratingStmt = connection.prepareStatement(ratingQuery);
                    ratingStmt.setInt(1, restaurantId);
                    ResultSet ratingRs = ratingStmt.executeQuery();
                    
                    double avgRating = 0.0;
                    if (ratingRs.next()) {
                        avgRating = ratingRs.getDouble("avg_rating");
                    }
                    
                    // Create the dimension record
                    String record = restaurantId + "," + restaurantName + "," + cuisineType + "," + String.format("%.2f", avgRating);
                    context.write(new Text(record), NullWritable.get());
                    
                    ratingRs.close();
                    ratingStmt.close();
                }
                
                rs.close();
                stmt.close();
            } catch (Exception e) {
                throw new IOException("Error processing restaurant data", e);
            }
        }
        
        @Override
        protected void cleanup(Context context) throws IOException, InterruptedException {
            try {
                if (connection != null && !connection.isClosed()) {
                    connection.close();
                }
            } catch (Exception e) {
                throw new IOException("Could not close database connection", e);
            }
        }
    }
    
    @Override
    protected String getExtractQuery() {
        return "SELECT restaurant_id, restaurant_name, cuisine_type FROM restaurants";
    }
    
    @Override
    protected String getOutputPath() {
        return DBConfig.DIM_RESTAURANT_PATH;
    }
    
    @Override
    protected String getJobName() {
        return "Restaurant Dimension Generator";
    }
    
    @Override
    protected Job configureJob(Configuration conf) throws Exception {
        Job job = Job.getInstance(conf, getJobName());
        job.setJarByClass(DimRestaurantGenerator.class);
        
        // Set the Mapper (no Reducer needed as we're just extracting and transforming)
        job.setMapperClass(RestaurantMapper.class);
        job.setNumReduceTasks(0);
        
        // Define the output
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(NullWritable.class);
        job.setOutputFormatClass(TextOutputFormat.class);
        
        // Set the output path
        FileOutputFormat.setOutputPath(job, new Path(getOutputPath()));
        
        return job;
    }
}
