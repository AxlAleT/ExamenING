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
 * MapReduce job to generate the DeliveryPerson dimension table
 * Since we don't have delivery person data in our source database,
 * we'll generate synthetic data for demonstration purposes
 */
public class DimDeliveryPersonGenerator extends BaseDimensionGenerator {
    
    /**
     * Mapper class that generates delivery person dimension records
     */
    public static class DeliveryPersonMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        private Connection connection;
        private Random random = new Random();
        
        // Sample first and last names for synthetic data
        private static final String[] FIRST_NAMES = {
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica"
        };
        
        private static final String[] LAST_NAMES = {
            "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
            "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"
        };
        
        private static final String[] OPERATION_ZONES = {
            "North Zone", "South Zone", "East Zone", "West Zone", "Central Zone",
            "Northwest", "Northeast", "Southwest", "Southeast", "Downtown"
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
                // Generate synthetic delivery person data
                // We'll create 30 delivery person records
                for (int deliveryPersonId = 1; deliveryPersonId <= 30; deliveryPersonId++) {
                    String firstName = FIRST_NAMES[random.nextInt(FIRST_NAMES.length)];
                    String lastName = LAST_NAMES[random.nextInt(LAST_NAMES.length)];
                    String deliveryPersonName = firstName + " " + lastName;
                    
                    String operationZone = OPERATION_ZONES[random.nextInt(OPERATION_ZONES.length)];
                    
                    // Generate random tenure in months (1-60 months)
                    int tenureMonths = 1 + random.nextInt(60);
                    
                    // Create the dimension record
                    String record = deliveryPersonId + "," + deliveryPersonName + "," + operationZone + "," + tenureMonths;
                    context.write(new Text(record), NullWritable.get());
                }
            } catch (Exception e) {
                throw new IOException("Error generating delivery person dimension data", e);
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
        return DBConfig.DIM_DELIVERYPERSON_PATH;
    }
    
    @Override
    protected String getJobName() {
        return "Delivery Person Dimension Generator";
    }
    
    @Override
    protected Job configureJob(Configuration conf) throws Exception {
        Job job = Job.getInstance(conf, getJobName());
        job.setJarByClass(DimDeliveryPersonGenerator.class);
        
        // Set the Mapper (no Reducer needed as we're just generating data)
        job.setMapperClass(DeliveryPersonMapper.class);
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
