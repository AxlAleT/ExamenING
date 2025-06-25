package com.hadoop.aggregation;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashSet;
import java.util.Set;

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
 * MapReduce job to generate the Date dimension table
 */
public class DimDateGenerator extends BaseDimensionGenerator {
    
    /**
     * Mapper class that generates date dimension records
     */
    public static class DateMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        private Connection connection;
        private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        private Calendar cal = Calendar.getInstance();
        
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
                // Query to get all day names
                String query = "SELECT day_id, day_name FROM days";
                PreparedStatement stmt = connection.prepareStatement(query);
                ResultSet rs = stmt.executeQuery();
                
                // Store all day names
                Set<String> dayNames = new HashSet<>();
                while (rs.next()) {
                    dayNames.add(rs.getString("day_name"));
                }
                rs.close();
                stmt.close();
                
                // Generate dates for a full year (current date - 6 months to current date + 6 months)
                Calendar startCal = Calendar.getInstance();
                startCal.add(Calendar.MONTH, -6);
                
                Calendar endCal = Calendar.getInstance();
                endCal.add(Calendar.MONTH, 6);
                
                // Create a sequential ID counter
                int dateId = 1;
                
                // Generate date records
                Calendar currentCal = (Calendar) startCal.clone();
                while (currentCal.before(endCal)) {
                    Date currentDate = currentCal.getTime();
                    String dateStr = dateFormat.format(currentDate);
                    
                    // Get day of week
                    cal.setTime(currentDate);
                    String[] daysOfWeek = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};
                    String dayOfWeek = daysOfWeek[cal.get(Calendar.DAY_OF_WEEK) - 1];
                    
                    // Get month and quarter
                    int month = cal.get(Calendar.MONTH) + 1; // Calendar months are 0-based
                    int quarter = ((month - 1) / 3) + 1;
                    String monthName = new SimpleDateFormat("MMMM").format(currentDate);
                    
                    // Get year
                    int year = cal.get(Calendar.YEAR);
                    
                    // Create the dimension record
                    String record = dateId + "," + dateStr + "," + dayOfWeek + "," + monthName + "," + quarter + "," + year;
                    context.write(new Text(record), NullWritable.get());
                    
                    // Increment counter and date
                    dateId++;
                    currentCal.add(Calendar.DATE, 1);
                }
            } catch (Exception e) {
                throw new IOException("Error generating date dimension data", e);
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
        return "SELECT day_id, day_name FROM days";
    }
    
    @Override
    protected String getOutputPath() {
        return DBConfig.DIM_DATE_PATH;
    }
    
    @Override
    protected String getJobName() {
        return "Date Dimension Generator";
    }
    
    @Override
    protected Job configureJob(Configuration conf) throws Exception {
        Job job = Job.getInstance(conf, getJobName());
        job.setJarByClass(DimDateGenerator.class);
        
        // Set the Mapper (no Reducer needed as we're just generating data)
        job.setMapperClass(DateMapper.class);
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
