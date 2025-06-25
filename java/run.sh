#!/bin/bash

# Build the project
mvn clean package

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful!"
    
    # Get command line arguments
    COMMAND=${1:-"process-all"}
    
    # Create output directories if they don't exist
    mkdir -p warehouse/fooddelivery/dim_customer
    mkdir -p warehouse/fooddelivery/dim_restaurant
    mkdir -p warehouse/fooddelivery/dim_date
    mkdir -p warehouse/fooddelivery/dim_location
    mkdir -p warehouse/fooddelivery/dim_timeslot
    mkdir -p warehouse/fooddelivery/dim_deliveryperson
    mkdir -p warehouse/fooddelivery/fact_orders
    
    # Remove previous outputs
    rm -rf warehouse/fooddelivery/dim_customer/*
    rm -rf warehouse/fooddelivery/dim_restaurant/*
    rm -rf warehouse/fooddelivery/dim_date/*
    rm -rf warehouse/fooddelivery/dim_location/*
    rm -rf warehouse/fooddelivery/dim_timeslot/*
    rm -rf warehouse/fooddelivery/dim_deliveryperson/*
    rm -rf warehouse/fooddelivery/fact_orders/*
    
    # Run the MapReduce job with the specified command
    echo "Running MapReduce job with command: $COMMAND"
    hadoop jar target/hadoop-aggregation-1.0-SNAPSHOT-jar-with-dependencies.jar com.hadoop.aggregation.AggregationDriver $COMMAND
    
    # Check if the job ran successfully
    if [ $? -eq 0 ]; then
        echo "Job completed successfully!"
        echo "Warehouse data created in warehouse/fooddelivery/"
        echo "Sample output:"
        
        # Display sample data from each dimension
        echo "Customer Dimension:"
        head -n 3 warehouse/fooddelivery/dim_customer/part-r-00000
        
        echo "Restaurant Dimension:"
        head -n 3 warehouse/fooddelivery/dim_restaurant/part-r-00000
        
        echo "Date Dimension:"
        head -n 3 warehouse/fooddelivery/dim_date/part-r-00000
        
        echo "Location Dimension:"
        head -n 3 warehouse/fooddelivery/dim_location/part-r-00000
        
        echo "TimeSlot Dimension:"
        head -n 3 warehouse/fooddelivery/dim_timeslot/part-r-00000
        
        echo "DeliveryPerson Dimension:"
        head -n 3 warehouse/fooddelivery/dim_deliveryperson/part-r-00000
        
        echo "Order Facts:"
        head -n 3 warehouse/fooddelivery/fact_orders/part-r-00000
    else
        echo "Job failed."
    fi
else
    echo "Build failed."
fi
