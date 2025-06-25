package com.hadoop.aggregation;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.Statement;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

/**
 * Utility to export dimension and fact tables from HDFS to MySQL
 */
public class DataWarehouseExporter extends Configured implements Tool {

    @Override
    public int run(String[] args) throws Exception {
        // Create database schema in target database
        createDatabaseSchema();
        
        // Export dimension tables
        exportDimensionTable("dim_customer", DIM_CUSTOMER_SCHEMA);
        exportDimensionTable("dim_restaurant", DIM_RESTAURANT_SCHEMA);
        exportDimensionTable("dim_date", DIM_DATE_SCHEMA);
        exportDimensionTable("dim_location", DIM_LOCATION_SCHEMA);
        exportDimensionTable("dim_timeslot", DIM_TIMESLOT_SCHEMA);
        exportDimensionTable("dim_deliveryperson", DIM_DELIVERYPERSON_SCHEMA);
        
        // Export fact table
        exportFactTable();
        
        return 0;
    }
    
    private void createDatabaseSchema() throws Exception {
        Class.forName(DBConfig.JDBC_DRIVER);
        try (Connection conn = DriverManager.getConnection(
                DBConfig.TARGET_DB_URL, 
                DBConfig.TARGET_DB_USER, 
                DBConfig.TARGET_DB_PASSWORD)) {
            
            Statement stmt = conn.createStatement();
            
            // Create dimension tables
            stmt.executeUpdate(DIM_CUSTOMER_SCHEMA);
            stmt.executeUpdate(DIM_RESTAURANT_SCHEMA);
            stmt.executeUpdate(DIM_DATE_SCHEMA);
            stmt.executeUpdate(DIM_LOCATION_SCHEMA);
            stmt.executeUpdate(DIM_TIMESLOT_SCHEMA);
            stmt.executeUpdate(DIM_DELIVERYPERSON_SCHEMA);
            
            // Create fact table
            stmt.executeUpdate(FACT_ORDERS_SCHEMA);
            
            stmt.close();
        }
    }
    
    private void exportDimensionTable(String tableName, String schema) throws Exception {
        String hdfsPath = DBConfig.HDFS_BASE_PATH + tableName;
        Configuration conf = getConf();
        FileSystem fs = FileSystem.get(conf);
        
        if (!fs.exists(new Path(hdfsPath))) {
            System.out.println("Path does not exist: " + hdfsPath);
            return;
        }
        
        FileStatus[] fileStatuses = fs.listStatus(new Path(hdfsPath));
        
        for (FileStatus status : fileStatuses) {
            if (!status.isDirectory() && !status.getPath().getName().startsWith("_")) {
                BufferedReader br = new BufferedReader(
                        new InputStreamReader(fs.open(status.getPath())));
                
                String line;
                while ((line = br.readLine()) != null) {
                    insertRecord(tableName, line);
                }
                
                br.close();
            }
        }
    }
    
    private void exportFactTable() throws Exception {
        exportDimensionTable("fact_orders", FACT_ORDERS_SCHEMA);
    }
    
    private void insertRecord(String tableName, String csvLine) throws Exception {
        String[] fields = csvLine.split(",");
        
        String insertSql = "";
        int fieldCount = fields.length;
        
        switch (tableName) {
            case "dim_customer":
                insertSql = "INSERT INTO dim_customer VALUES (?, ?, ?, ?)";
                break;
            case "dim_restaurant":
                insertSql = "INSERT INTO dim_restaurant VALUES (?, ?, ?, ?)";
                break;
            case "dim_date":
                insertSql = "INSERT INTO dim_date VALUES (?, ?, ?, ?, ?, ?)";
                break;
            case "dim_location":
                insertSql = "INSERT INTO dim_location VALUES (?, ?, ?, ?, ?)";
                break;
            case "dim_timeslot":
                insertSql = "INSERT INTO dim_timeslot VALUES (?, ?, ?, ?)";
                break;
            case "dim_deliveryperson":
                insertSql = "INSERT INTO dim_deliveryperson VALUES (?, ?, ?, ?)";
                break;
            case "fact_orders":
                insertSql = "INSERT INTO fact_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
                break;
        }
        
        Connection conn = DriverManager.getConnection(
                DBConfig.TARGET_DB_URL, 
                DBConfig.TARGET_DB_USER, 
                DBConfig.TARGET_DB_PASSWORD);
        
        PreparedStatement pstmt = conn.prepareStatement(insertSql);
        
        for (int i = 0; i < fieldCount; i++) {
            String value = fields[i].trim();
            if (value.equals("NULL")) {
                pstmt.setNull(i + 1, java.sql.Types.NULL);
            } else {
                pstmt.setString(i + 1, value);
            }
        }
        
        pstmt.executeUpdate();
        pstmt.close();
        conn.close();
    }
    
    // SQL schemas for tables
    private static final String DIM_CUSTOMER_SCHEMA = 
            "CREATE TABLE IF NOT EXISTS dim_customer (" +
            "  customer_id INT PRIMARY KEY," +
            "  customer_name VARCHAR(255)," +
            "  segment VARCHAR(50)," +
            "  registration_date DATE" +
            ")";
    
    private static final String DIM_RESTAURANT_SCHEMA = 
            "CREATE TABLE IF NOT EXISTS dim_restaurant (" +
            "  restaurant_id INT PRIMARY KEY," +
            "  restaurant_name VARCHAR(255)," +
            "  cuisine_type VARCHAR(100)," +
            "  rating_avg DECIMAL(3,2)" +
            ")";
    
    private static final String DIM_DATE_SCHEMA = 
            "CREATE TABLE IF NOT EXISTS dim_date (" +
            "  date_id INT PRIMARY KEY," +
            "  full_date DATE," +
            "  day_of_week VARCHAR(20)," +
            "  month_name VARCHAR(20)," +
            "  quarter INT," +
            "  year INT" +
            ")";
    
    private static final String DIM_LOCATION_SCHEMA = 
            "CREATE TABLE IF NOT EXISTS dim_location (" +
            "  location_id INT PRIMARY KEY," +
            "  neighborhood VARCHAR(100)," +
            "  postal_code VARCHAR(20)," +
            "  city VARCHAR(100)," +
            "  region VARCHAR(100)" +
            ")";
    
    private static final String DIM_TIMESLOT_SCHEMA = 
            "CREATE TABLE IF NOT EXISTS dim_timeslot (" +
            "  time_slot_id INT PRIMARY KEY," +
            "  slot_name VARCHAR(50)," +
            "  start_time TIME," +
            "  end_time TIME" +
            ")";
    
    private static final String DIM_DELIVERYPERSON_SCHEMA = 
            "CREATE TABLE IF NOT EXISTS dim_deliveryperson (" +
            "  delivery_person_id INT PRIMARY KEY," +
            "  delivery_person_name VARCHAR(255)," +
            "  operation_zone VARCHAR(100)," +
            "  tenure_months INT" +
            ")";
    
    private static final String FACT_ORDERS_SCHEMA = 
            "CREATE TABLE IF NOT EXISTS fact_orders (" +
            "  order_id INT," +
            "  customer_id INT," +
            "  restaurant_id INT," +
            "  delivery_person_id INT," +
            "  date_id INT," +
            "  location_id INT," +
            "  time_slot_id INT," +
            "  order_date DATE," +
            "  order_time TIME," +
            "  order_cost DECIMAL(10,2)," +
            "  rating INT," +
            "  food_preparation_time INT," +
            "  delivery_time INT," +
            "  total_time INT," +
            "  PRIMARY KEY (order_id)," +
            "  FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)," +
            "  FOREIGN KEY (restaurant_id) REFERENCES dim_restaurant(restaurant_id)," +
            "  FOREIGN KEY (delivery_person_id) REFERENCES dim_deliveryperson(delivery_person_id)," +
            "  FOREIGN KEY (date_id) REFERENCES dim_date(date_id)," +
            "  FOREIGN KEY (location_id) REFERENCES dim_location(location_id)," +
            "  FOREIGN KEY (time_slot_id) REFERENCES dim_timeslot(time_slot_id)" +
            ")";
    
    public static void main(String[] args) throws Exception {
        int result = ToolRunner.run(new Configuration(), new DataWarehouseExporter(), args);
        System.exit(result);
    }
}
