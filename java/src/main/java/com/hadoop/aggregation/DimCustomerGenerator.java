package com.hadoop.aggregation;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Date;
import java.text.SimpleDateFormat;

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
 * MapReduce job to generate the Customer dimension table
 */
public class DimCustomerGenerator extends BaseDimensionGenerator {
    
    /**
     * Mapper class that reads from MySQL and emits customer dimension records
     */
    public static class CustomerMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        private Connection connection;
        private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        
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
                // Query to get customer data
                String query = "SELECT customer_id FROM customers";
                PreparedStatement stmt = connection.prepareStatement(query);
                ResultSet rs = stmt.executeQuery();
                
                // Generate customer dimension records
                // Since our database doesn't have all the fields in the dimension,
                // we'll generate some sample data
                while (rs.next()) {
                    int customerId = rs.getInt("customer_id");
                    
                    // Generate sample data (in a real scenario, this would come from the database)
                    String customerName = "Customer " + customerId;
                    String segment = (customerId % 3 == 0) ? "Premium" : (customerId % 2 == 0) ? "Regular" : "Basic";
                    
                    // Generate a random registration date within the last 2 years
                    long now = System.currentTimeMillis();
                    long twoYearsAgo = now - (2L * 365 * 24 * 60 * 60 * 1000);
                    long randomTime = twoYearsAgo + (long)(Math.random() * (now - twoYearsAgo));
                    String registrationDate = dateFormat.format(new Date(randomTime));
                    
                    // Create the dimension record
                    String record = customerId + "," + customerName + "," + segment + "," + registrationDate;
                    context.write(new Text(record), NullWritable.get());
                }
                
                rs.close();
                stmt.close();
            } catch (Exception e) {
                throw new IOException("Error processing customer data", e);
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
        return "SELECT customer_id FROM customers";
    }
    
    @Override
    protected String getOutputPath() {
        return DBConfig.DIM_CUSTOMER_PATH;
    }
    
    @Override
    protected String getJobName() {
        return "Customer Dimension Generator";
    }
    
    @Override
    protected Job configureJob(Configuration conf) throws Exception {
        Job job = Job.getInstance(conf, getJobName());
        job.setJarByClass(DimCustomerGenerator.class);
        
        // Set the Mapper (no Reducer needed as we're just extracting and transforming)
        job.setMapperClass(CustomerMapper.class);
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
