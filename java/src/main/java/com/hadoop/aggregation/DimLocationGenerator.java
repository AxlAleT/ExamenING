package com.hadoop.aggregation;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.util.Random;

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
 * MapReduce job to generate the Location dimension table
 * Since we don't have location data in our source database,
 * we'll generate synthetic data for demonstration purposes
 */
public class DimLocationGenerator extends BaseDimensionGenerator {
    
    /**
     * Mapper class that generates location dimension records
     */
    public static class LocationMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        private Connection connection;
        private Random random = new Random();
        
        // Sample neighborhoods, postal codes, cities, and regions
        private static final String[] NEIGHBORHOODS = {
            "Downtown", "Uptown", "West End", "East Side", "North Hills", 
            "South Park", "Riverside", "Central District", "Harbor View", "Lake City"
        };
        
        private static final String[] CITIES = {
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"
        };
        
        private static final String[] REGIONS = {
            "Northeast", "Southeast", "Midwest", "Southwest", "West"
        };
        
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
                // Generate synthetic location data
                // We'll create 50 location records
                for (int locationId = 1; locationId <= 50; locationId++) {
                    String neighborhood = NEIGHBORHOODS[random.nextInt(NEIGHBORHOODS.length)];
                    String postalCode = String.format("%05d", 10000 + random.nextInt(90000));
                    String city = CITIES[random.nextInt(CITIES.length)];
                    String region = REGIONS[random.nextInt(REGIONS.length)];
                    
                    // Create the dimension record
                    String record = locationId + "," + neighborhood + "," + postalCode + "," + city + "," + region;
                    context.write(new Text(record), NullWritable.get());
                }
            } catch (Exception e) {
                throw new IOException("Error generating location dimension data", e);
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
        // No query needed for synthetic data
        return "";
    }
    
    @Override
    protected String getOutputPath() {
        return DBConfig.DIM_LOCATION_PATH;
    }
    
    @Override
    protected String getJobName() {
        return "Location Dimension Generator";
    }
    
    @Override
    protected Job configureJob(Configuration conf) throws Exception {
        Job job = Job.getInstance(conf, getJobName());
        job.setJarByClass(DimLocationGenerator.class);
        
        // Set the Mapper (no Reducer needed as we're just generating data)
        job.setMapperClass(LocationMapper.class);
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
