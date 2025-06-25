<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Hadoop MapReduce Aggregation Project

This is a Maven-based Hadoop MapReduce project. The project is structured to perform data aggregation operations by:
1. Reading input data with four fields (3 dimensions and 1 metric)
2. Grouping by the dimensions
3. Aggregating (summing) the metric values

## Key Components

- `AggregationDriver.java`: Main class that configures and runs the MapReduce job
- `AggregationMapper.java`: Maps input records to key-value pairs
- `AggregationReducer.java`: Reduces (aggregates) values with the same key

## Technologies

- Java 8
- Apache Hadoop 3.3.4
- Maven for dependency management and building

When suggesting code, please focus on Hadoop MapReduce best practices and efficient data processing techniques.
