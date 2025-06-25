package com.hadoop.aggregation;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.text.SimpleDateFormat;
import java.util.Calendar;

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
 * MapReduce job to generate the TimeSlot dimension table
 */
public class DimTimeSlotGenerator extends BaseDimensionGenerator {
    
    /**
     * Mapper class that generates time slot dimension records
     */
    public static class TimeSlotMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        private Connection connection;
        private SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");
        
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
                // Generate time slots at 30-minute intervals for a full day
                Calendar cal = Calendar.getInstance();
                cal.set(Calendar.HOUR_OF_DAY, 0);
                cal.set(Calendar.MINUTE, 0);
                cal.set(Calendar.SECOND, 0);
                cal.set(Calendar.MILLISECOND, 0);
                
                // Loop through each 30-minute time slot in a day
                int timeSlotId = 1;
                for (int hour = 0; hour < 24; hour++) {
                    for (int minute = 0; minute < 60; minute += 30) {
                        cal.set(Calendar.HOUR_OF_DAY, hour);
                        cal.set(Calendar.MINUTE, minute);
                        
                        String startTime = timeFormat.format(cal.getTime());
                        
                        // Add 30 minutes for end time
                        cal.add(Calendar.MINUTE, 30);
                        String endTime = timeFormat.format(cal.getTime());
                        
                        // Set back to original time for next iteration
                        cal.add(Calendar.MINUTE, -30);
                        
                        // Create slot name
                        String slotName = "";
                        if (hour < 6) {
                            slotName = "Early Morning";
                        } else if (hour < 11) {
                            slotName = "Morning";
                        } else if (hour < 14) {
                            slotName = "Lunch";
                        } else if (hour < 17) {
                            slotName = "Afternoon";
                        } else if (hour < 20) {
                            slotName = "Evening";
                        } else {
                            slotName = "Night";
                        }
                        
                        // Create the dimension record
                        String record = timeSlotId + "," + slotName + "," + startTime + "," + endTime;
                        context.write(new Text(record), NullWritable.get());
                        
                        // Increment ID
                        timeSlotId++;
                    }
                }
            } catch (Exception e) {
                throw new IOException("Error generating time slot dimension data", e);
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
        // No query needed for time slots
        return "";
    }
    
    @Override
    protected String getOutputPath() {
        return DBConfig.DIM_TIMESLOT_PATH;
    }
    
    @Override
    protected String getJobName() {
        return "Time Slot Dimension Generator";
    }
    
    @Override
    protected Job configureJob(Configuration conf) throws Exception {
        Job job = Job.getInstance(conf, getJobName());
        job.setJarByClass(DimTimeSlotGenerator.class);
        
        // Set the Mapper (no Reducer needed as we're just generating data)
        job.setMapperClass(TimeSlotMapper.class);
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
