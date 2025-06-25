# Food Delivery Data Warehouse

A Hadoop-based data warehouse for food delivery data, implementing a star schema with dimension and fact tables.

## Project Overview

This project implements a data warehouse for food delivery data using Hadoop MapReduce. It:

1. Extracts data from a MySQL database containing food delivery orders
2. Transforms the data into a star schema model with dimension and fact tables
3. Loads the data into HDFS as the foundation for data warehouse analytics

## Star Schema Design (Esquema Estelar)

### Tabla de Hechos (Fact Table)
- **Fact_Pedidos**: Contiene las métricas principales del negocio
  - *Métricas*: monto_pedido, tiempo_preparacion, tiempo_entrega, calificacion
  - *Claves foráneas*: Enlaces a todas las dimensiones

### Dimensiones (Dimensions)
- **dim_Cliente**: Segmento, antigüedad del cliente
- **dim_Restaurante**: Tipo de cocina, capacidad
- **dim_Repartidor**: Experiencia, zona asignada
- **dim_Tiempo**: Día de la semana, hora, temporada
- **dim_Ubicación**: Barrio, código postal, región
- **dim_TimeSlot**: Segmentos horarios del día

Para ver el diagrama y la descripción detallada del esquema, consulte los archivos:
- `star_schema_diagram.md`: Diagrama visual del esquema estrella
- `STAR_SCHEMA_DESCRIPTION.md`: Descripción detallada de todas las tablas y su propósito

Para generar la documentación del esquema:
```bash
./generate_schema.sh
```

## Requirements

- Java 8 or higher
- Maven 3.6 or higher
- Hadoop 3.x
- MySQL database with food delivery data

## Building the Project

```bash
mvn clean package
```

This will create a JAR file with dependencies in the `target` folder.

## Running the ETL Process

### Process All Tables
```bash
./run.sh process-all
```

### Process Only Dimension Tables
```bash
./run.sh create-dimensions
```

### Process Only Fact Table
```bash
./run.sh create-fact
```

### Generate Star Schema Documentation
```bash
./run.sh generate-schema
```

## Output Data

The data warehouse tables are created in the HDFS directory structure:
```
/warehouse/fooddelivery/
  dim_customer/
  dim_restaurant/
  dim_date/
  dim_location/
  dim_timeslot/
  dim_deliveryperson/
  fact_orders/
```

## Database Schema

The source database contains the following tables:
- customers (customer_id, first_name, last_name, email, phone, address, city, registration_date)
- restaurants (restaurant_id, restaurant_name, cuisine_type, address, city, phone, website, price_range, rating_avg, opening_hour, closing_hour, established_date)
- days (day_id, day_name, is_weekend, is_holiday)
- delivery_person (delivery_person_id, first_name, last_name, phone, email, vehicle_type, hire_date, rating)
- orders (order_id, customer_id, restaurant_id, day_id, cost_of_the_order, rating, food_preparation_time, delivery_time, delivery_person_id, tip_amount)

## Preguntas de Negocio

El esquema está optimizado para responder preguntas de negocio como:

1. ¿Cuáles son los restaurantes con mejor/peor desempeño en tiempos de preparación?
2. ¿Cómo varía el tiempo de entrega por zona geográfica?
3. ¿Qué segmento de clientes genera más ingresos?
4. ¿En qué días y horarios se concentran los pedidos?
5. ¿Cómo se correlacionan las calificaciones con los tiempos de entrega?
