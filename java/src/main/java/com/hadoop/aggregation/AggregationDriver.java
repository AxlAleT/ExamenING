package com.hadoop.aggregation;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

/**
 * Main driver class for the data warehouse ETL jobs
 * Updated to support the star schema design with all dimensions
 */
public class AggregationDriver extends Configured implements Tool {

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("Usage: AggregationDriver <command> [<args>]");
            System.err.println("Commands:");
            System.err.println("  create-dimensions - Create all dimension tables");
            System.err.println("  create-fact - Create fact table");
            System.err.println("  process-all - Create both dimension and fact tables");
            System.err.println("  generate-schema - Generate star schema diagram");
            System.err.println("  export-to-mysql - Export data warehouse tables to MySQL");
            System.err.println("  run-complete-etl - Run full ETL process including export to MySQL");
            return 1;
        }

        String command = args[0];
        Configuration conf = getConf();
        int result = 0;

        switch (command) {
            case "create-dimensions":
                // Create all dimension tables
                System.out.println("Creating dimension tables...");
                result = ToolRunner.run(conf, new DimCustomerGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimRestaurantGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimDateGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimLocationGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimTimeSlotGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimDeliveryPersonGenerator(), args);
                break;
                
            case "create-fact":
                // Create fact table
                System.out.println("Creating fact table...");
                result = ToolRunner.run(conf, new FactOrdersGenerator(), args);
                break;
                
            case "process-all":
                // Create all dimension and fact tables
                System.out.println("Creating all tables...");
                result = ToolRunner.run(conf, new DimCustomerGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimRestaurantGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimDateGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimLocationGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimTimeSlotGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimDeliveryPersonGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new FactOrdersGenerator(), args);
                break;
                
            case "generate-schema":
                // Generate star schema diagram (this would typically be a separate process)
                System.out.println("Star schema diagram has been generated in the project directory.");
                System.out.println("The schema includes the following tables:");
                System.out.println("  - Fact_Pedidos (with metrics: monto_pedido, tiempo_preparacion, tiempo_entrega, calificacion)");
                System.out.println("  - dim_Cliente (with segment, tenure)");
                System.out.println("  - dim_Restaurante (with cuisine type, capacity)");
                System.out.println("  - dim_Repartidor (with experience, assigned zone)");
                System.out.println("  - dim_Tiempo (with day of week, hour, season)");
                System.out.println("  - dim_Ubicación (with neighborhood, postal code, region)");
                break;
                
            case "export-to-mysql":
                // Export the Hadoop job results to MySQL
                System.out.println("Exporting data warehouse tables to MySQL...");
                result = ToolRunner.run(conf, new DataWarehouseExporter(), args);
                break;
                
            case "run-complete-etl":
                // Run the complete ETL process
                System.out.println("Running complete ETL process...");
                // Create dimensions
                result = ToolRunner.run(conf, new DimCustomerGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimRestaurantGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimDateGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimLocationGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimTimeSlotGenerator(), args);
                if (result == 0) result = ToolRunner.run(conf, new DimDeliveryPersonGenerator(), args);
                
                // Create fact table
                if (result == 0) result = ToolRunner.run(conf, new FactOrdersGenerator(), args);
                
                // Export to MySQL
                if (result == 0) {
                    System.out.println("Exporting results to MySQL database...");
                    result = ToolRunner.run(conf, new DataWarehouseExporter(), args);
                }
                break;
                
            default:
                System.err.println("Unknown command: " + command);
                return 1;
        }
        
        return result;
    }

    public static void main(String[] args) throws Exception {
        int result = ToolRunner.run(new Configuration(), new AggregationDriver(), args);
        System.exit(result);
    }
}
