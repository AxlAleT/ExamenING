package com.hadoop.aggregation;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Map;
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
 * MapReduce job to generate the fact table for orders
 */
public class FactOrdersGenerator extends BaseDimensionGenerator {
    
    /**
     * Mapper class that reads from MySQL and emits fact table records
     */
    public static class FactOrdersMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        private Connection connection;
        private Random random = new Random();
        private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        private SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");
        
        // Maps to store dimension lookups
        private Map<Integer, Integer> customerDimMap = new HashMap<>();
        private Map<Integer, Integer> restaurantDimMap = new HashMap<>();
        private Map<Integer, Integer> dayToDimDateMap = new HashMap<>();
        private Map<String, Integer> timeToTimeSlotMap = new HashMap<>();
        
        @Override
        protected void setup(Context context) throws IOException, InterruptedException {
            try {
                // Get database connection
                Class.forName(DBConfig.JDBC_DRIVER);
                connection = DriverManager.getConnection(DBConfig.DB_URL, DBConfig.DB_USER, DBConfig.DB_PASSWORD);
                
                // Pre-load mappings (in a real scenario, this would use distributed cache)
                // For this example, we'll assume dimensions match 1:1 with source data
                // In reality, you'd load these from the dimension tables in HDFS
                
                // For simplicity, we'll use 1:1 mapping for customers and restaurants
                // We'll randomly assign locations and delivery persons
            } catch (Exception e) {
                throw new IOException("Could not connect to database", e);
            }
        }
        
        @Override
        protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            try {
                // Query to get orders data
                String query = "SELECT o.order_id, o.customer_id, o.restaurant_id, o.day_id, " +
                               "o.cost_of_the_order, o.rating, o.food_preparation_time, o.delivery_time, " +
                               "d.day_name " +
                               "FROM orders o " +
                               "JOIN days d ON o.day_id = d.day_id";
                               
                PreparedStatement stmt = connection.prepareStatement(query);
                ResultSet rs = stmt.executeQuery();
                
                // Generate fact table records
                while (rs.next()) {
                    int orderId = rs.getInt("order_id");
                    int customerId = rs.getInt("customer_id");
                    int restaurantId = rs.getInt("restaurant_id");
                    int dayId = rs.getInt("day_id");
                    double orderCost = rs.getDouble("cost_of_the_order");
                    
                    Integer rating = null;
                    if (rs.getObject("rating") != null) {
                        rating = rs.getInt("rating");
                    }
                    
                    int prepTime = rs.getInt("food_preparation_time");
                    int deliveryTime = rs.getInt("delivery_time");
                    String dayName = rs.getString("day_name");
                    
                    // Generate random dimensions for those not in source data
                    
                    // Random location ID (1-50)
                    int locationId = 1 + random.nextInt(50);
                    
                    // Random delivery person ID (1-30)
                    int deliveryPersonId = 1 + random.nextInt(30);
                    
                    // Generate random order date based on day of week
                    Calendar cal = Calendar.getInstance();
                    cal.add(Calendar.DATE, -random.nextInt(60)); // Random date in last 60 days
                    
                    // Adjust to match day of week
                    int dayOfWeek = getDayOfWeekFromName(dayName);
                    while (cal.get(Calendar.DAY_OF_WEEK) != dayOfWeek) {
                        cal.add(Calendar.DATE, -1);
                    }
                    String orderDate = dateFormat.format(cal.getTime());
                    
                    // Generate random order time
                    cal.set(Calendar.HOUR_OF_DAY, 10 + random.nextInt(12)); // Between 10 AM and 10 PM
                    cal.set(Calendar.MINUTE, random.nextInt(60));
                    cal.set(Calendar.SECOND, random.nextInt(60));
                    String orderTime = timeFormat.format(cal.getTime());
                    
                    // Map to time slot ID (for simplicity, we'll use hour / 2 + 1)
                    int hour = cal.get(Calendar.HOUR_OF_DAY);
                    int timeSlotId = (hour / 2) + 1;
                    
                    // For our data warehouse dateId, we'll use a simple mapping based on orderId
                    // In a real scenario, you'd look up the proper date dimension ID
                    int dateId = (orderId % 365) + 1;
                    
                    // Create the fact record (CSV format)
                    String factRecord = orderId + "," + 
                                       customerId + "," + 
                                       restaurantId + "," + 
                                       deliveryPersonId + "," +
                                       dateId + "," +
                                       locationId + "," +
                                       timeSlotId + "," +
                                       orderDate + "," +
                                       orderTime + "," +
                                       orderCost + "," +
                                       (rating != null ? rating : "NULL") + "," +
                                       prepTime + "," +
                                       deliveryTime + "," +
                                       (prepTime + deliveryTime);
                    
                    context.write(new Text(factRecord), NullWritable.get());
                }
                
                rs.close();
                stmt.close();
            } catch (Exception e) {
                throw new IOException("Error processing order fact data", e);
            }
        }
        
        private int getDayOfWeekFromName(String dayName) {
            switch (dayName.toLowerCase()) {
                case "sunday": return Calendar.SUNDAY;
                case "monday": return Calendar.MONDAY;
                case "tuesday": return Calendar.TUESDAY;
                case "wednesday": return Calendar.WEDNESDAY;
                case "thursday": return Calendar.THURSDAY;
                case "friday": return Calendar.FRIDAY;
                case "saturday": return Calendar.SATURDAY;
                default: return Calendar.MONDAY; // Default to Monday
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
        return "SELECT o.order_id, o.customer_id, o.restaurant_id, o.day_id, " +
               "o.cost_of_the_order, o.rating, o.food_preparation_time, o.delivery_time, " +
               "d.day_name " +
               "FROM orders o " +
               "JOIN days d ON o.day_id = d.day_id";
    }
    
    @Override
    protected String getOutputPath() {
        return DBConfig.FACT_ORDERS_PATH;
    }
    
    @Override
    protected String getJobName() {
        return "Order Facts Generator";
    }
    
    @Override
    protected Job configureJob(Configuration conf) throws Exception {
        Job job = Job.getInstance(conf, getJobName());
        job.setJarByClass(FactOrdersGenerator.class);
        
        // Set the Mapper (no Reducer needed as we're just extracting and transforming)
        job.setMapperClass(FactOrdersMapper.class);
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
