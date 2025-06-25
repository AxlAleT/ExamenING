package com.hadoop.aggregation;

import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.Mapper;
import java.io.IOException;

/**
 * Mapper class for the data aggregation job
 * Parses input lines with format: dimension1,dimension2,dimension3,metric
 */
public class AggregationMapper extends Mapper<LongWritable, Text, Text, DoubleWritable> {
    private Text dimensionKey = new Text();
    private DoubleWritable metricValue = new DoubleWritable();
    
    @Override
    public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String[] parts = value.toString().split(",");
        if (parts.length == 4) {
            String d1 = parts[0].trim();
            String d2 = parts[1].trim();
            String d3 = parts[2].trim();
            double m1 = Double.parseDouble(parts[3].trim());
            
            dimensionKey.set(d1 + "," + d2 + "," + d3);
            metricValue.set(m1);
            context.write(dimensionKey, metricValue);
        }
    }
}
