# Hadoop Data Aggregation

A MapReduce application for aggregating data based on dimensions.

## Project Overview

This project implements a Hadoop MapReduce job that:
1. Reads input data in the format: `dimension1,dimension2,dimension3,metric`
2. Groups the data by the combination of all three dimensions 
3. Sums the metric values for each unique dimension combination
4. Outputs the results as `dimension1,dimension2,dimension3 \t sum_of_metrics`

## Requirements

- Java 8 or higher
- Maven 3.6 or higher
- Hadoop 3.x (for running in a Hadoop cluster)

## Building the Project

```bash
mvn clean package
```

This will create a JAR file with dependencies in the `target` folder.

## Running the Job

### Local Mode (for testing)

```bash
hadoop jar target/hadoop-aggregation-1.0-SNAPSHOT-jar-with-dependencies.jar com.hadoop.aggregation.AggregationDriver input_directory output_directory
```

### On a Hadoop Cluster

```bash
hadoop jar target/hadoop-aggregation-1.0-SNAPSHOT-jar-with-dependencies.jar com.hadoop.aggregation.AggregationDriver /path/to/input /path/to/output
```

## Input Data Format

The input data should be in CSV format with four fields:
```
dimension1,dimension2,dimension3,metric
```

Example:
```
product1,region1,category1,100.5
product1,region1,category2,200.3
product2,region2,category1,150.0
```

## Output Data Format

The output will be in the format:
```
dimension1,dimension2,dimension3    sum_of_metrics
```

Example:
```
product1,region1,category1    100.5
product1,region1,category2    200.3
product2,region2,category1    150.0
```
