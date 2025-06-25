package com.hadoop.aggregation;

/**
 * Configuration constants for database connection
 */
public class DBConfig {
    // Database connection properties for source database
    public static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";
    public static final String DB_URL = "jdbc:mysql://db:3306/ordersdb";
    public static final String DB_USER = "root";
    public static final String DB_PASSWORD = "example";
    
    // Database connection properties for target database
    public static final String TARGET_DB_URL = "jdbc:mysql://db:3306/datawarehouse";
    public static final String TARGET_DB_USER = "root";
    public static final String TARGET_DB_PASSWORD = "example";
    
    // HDFS paths for dimension tables
    public static final String HDFS_BASE_PATH = "/warehouse/fooddelivery/";
    public static final String DIM_CUSTOMER_PATH = HDFS_BASE_PATH + "dim_customer";
    public static final String DIM_RESTAURANT_PATH = HDFS_BASE_PATH + "dim_restaurant";
    public static final String DIM_DATE_PATH = HDFS_BASE_PATH + "dim_date";
    public static final String DIM_LOCATION_PATH = HDFS_BASE_PATH + "dim_location";
    public static final String DIM_TIMESLOT_PATH = HDFS_BASE_PATH + "dim_timeslot";
    public static final String DIM_DELIVERYPERSON_PATH = HDFS_BASE_PATH + "dim_deliveryperson";
    public static final String FACT_ORDERS_PATH = HDFS_BASE_PATH + "fact_orders";
    
    // Results export path
    public static final String RESULTS_PATH = HDFS_BASE_PATH + "results";
}
