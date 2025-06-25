#!/bin/bash

# Script to generate the star schema documentation and diagram

echo "Generating Star Schema Documentation and Diagram..."

# Set directory paths
JAVA_DIR="$(pwd)/java"
TARGET_DIR="$JAVA_DIR/target"
SRC_DIR="$JAVA_DIR/src"

# Compile the Java code if needed
echo "Compiling Java code..."
cd $JAVA_DIR
mvn clean package

# Run the AggregationDriver with the generate-schema command
echo "Running the schema generator..."
java -cp "$TARGET_DIR/fooddelivery-dw-1.0-SNAPSHOT.jar:$TARGET_DIR/dependency/*" com.hadoop.aggregation.AggregationDriver generate-schema

echo "Schema documentation and diagram have been generated in the project directory."
echo "Files created:"
echo "  - $JAVA_DIR/star_schema_diagram.md"
echo "  - $JAVA_DIR/STAR_SCHEMA_DESCRIPTION.md"

# Display instructions for viewing the diagram
echo ""
echo "To view the star schema diagram:"
echo "1. Open the file 'star_schema_diagram.md' in VS Code or a Markdown viewer that supports Mermaid diagrams"
echo "2. You can also use online Mermaid editors like https://mermaid.live"
echo ""
echo "Done."
