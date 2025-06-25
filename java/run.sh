#!/bin/bash

# Build the project
mvn clean package

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful!"
    
    # Create output directory if it doesn't exist
    mkdir -p output
    
    # Remove previous output
    rm -rf output/*
    
    # Run the MapReduce job with sample input
    echo "Running MapReduce job..."
    hadoop jar target/hadoop-aggregation-1.0-SNAPSHOT-jar-with-dependencies.jar com.hadoop.aggregation.AggregationDriver sample_input.txt output
    
    # Check if the job ran successfully
    if [ $? -eq 0 ]; then
        echo "Job completed successfully!"
        echo "Output:"
        cat output/part-r-00000
    else
        echo "Job failed."
    fi
else
    echo "Build failed."
fi
