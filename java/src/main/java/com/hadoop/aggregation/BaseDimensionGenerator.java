package com.hadoop.aggregation;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.util.Tool;

/**
 * Base class for all dimension generators
 */
public abstract class BaseDimensionGenerator extends Configured implements Tool {
    
    /**
     * Get a connection to the MySQL database
     */
    protected Connection getConnection() throws SQLException, ClassNotFoundException {
        Class.forName(DBConfig.JDBC_DRIVER);
        return DriverManager.getConnection(DBConfig.DB_URL, DBConfig.DB_USER, DBConfig.DB_PASSWORD);
    }
    
    /**
     * Get the SQL query to extract data for this dimension
     */
    protected abstract String getExtractQuery();
    
    /**
     * Get the HDFS output path for this dimension
     */
    protected abstract String getOutputPath();
    
    /**
     * Get the job name for this dimension generator
     */
    protected abstract String getJobName();
    
    /**
     * Configure the MapReduce job for this dimension
     */
    protected abstract Job configureJob(Configuration conf) throws Exception;
    
    @Override
    public int run(String[] args) throws Exception {
        Configuration conf = getConf();
        Job job = configureJob(conf);
        
        return job.waitForCompletion(true) ? 0 : 1;
    }
}
