# Diseño del Esquema Estrella para Sistema de Pedidos de Comida

## Introducción

Este documento presenta el diseño del esquema estrella para el sistema de pedidos de comida a domicilio. El esquema está optimizado para análisis de datos y consultas de negocio, permitiendo un análisis eficiente de métricas clave como montos de pedidos, tiempos de preparación, tiempos de entrega y calificaciones.

## Tabla de Hechos: Fact_Pedidos

La tabla de hechos central contiene las métricas de negocio principales y las claves foráneas a todas las dimensiones:

**Fact_Pedidos**
- **Claves primarias/foráneas:**
  - `order_id` (PK)
  - `customer_id` (FK → dim_Cliente)
  - `restaurant_id` (FK → dim_Restaurante)
  - `delivery_person_id` (FK → dim_Repartidor)
  - `date_id` (FK → dim_Tiempo)
  - `location_id` (FK → dim_Ubicación)
  - `time_slot_id` (FK → dim_TimeSlot)

- **Métricas:**
  - `monto_pedido`: Costo total del pedido
  - `tiempo_preparacion`: Tiempo que toma preparar la comida
  - `tiempo_entrega`: Tiempo que toma entregar el pedido
  - `calificacion`: Valoración del cliente (1-5)
  - `tiempo_total`: Tiempo total del pedido (preparación + entrega)

## Tablas de Dimensiones

### dim_Cliente
Contiene información sobre los clientes y su segmentación:
- `customer_id` (PK)
- `customer_name`: Nombre completo del cliente
- `segment`: Segmentación del cliente (Premium, Regular, Básico)
- `registration_date`: Fecha de registro
- `customer_tenure`: Antigüedad del cliente en días/meses

### dim_Restaurante
Información sobre los restaurantes:
- `restaurant_id` (PK)
- `restaurant_name`: Nombre del restaurante
- `cuisine_type`: Tipo de cocina
- `rating_avg`: Calificación promedio
- `capacity`: Capacidad de preparación (pedidos por hora)

### dim_Repartidor
Información sobre los repartidores:
- `delivery_person_id` (PK)
- `delivery_person_name`: Nombre del repartidor
- `operation_zone`: Zona de operación asignada
- `tenure_months`: Experiencia en meses
- `vehicle_type`: Tipo de vehículo
- `rating`: Calificación promedio

### dim_Tiempo
Dimensión temporal para análisis por fechas:
- `date_id` (PK)
- `full_date`: Fecha completa
- `day_of_week`: Día de la semana
- `month_name`: Nombre del mes
- `quarter`: Trimestre
- `year`: Año
- `is_weekend`: Indicador de fin de semana
- `is_holiday`: Indicador de día festivo
- `season`: Temporada (Verano, Otoño, Invierno, Primavera)

### dim_Ubicación
Información geográfica:
- `location_id` (PK)
- `neighborhood`: Barrio
- `postal_code`: Código postal
- `city`: Ciudad
- `region`: Región geográfica

### dim_TimeSlot
Segmentación horaria para análisis por hora del día:
- `time_slot_id` (PK)
- `slot_name`: Nombre del segmento horario (Mañana, Tarde, Noche)
- `start_time`: Hora de inicio
- `end_time`: Hora de fin

## Preguntas de Negocio que el Esquema Puede Responder

Este esquema estrella está optimizado para responder preguntas como:

1. ¿Cuáles son los restaurantes con mejor/peor desempeño en términos de tiempo de preparación?
2. ¿Cómo varía el tiempo de entrega por zona geográfica?
3. ¿Cuál es el segmento de clientes que realiza más pedidos y cuál genera más ingresos?
4. ¿Qué días de la semana y franjas horarias tienen mayor volumen de pedidos?
5. ¿Cómo se correlacionan las calificaciones con los tiempos de entrega?
6. ¿Cuál es el desempeño de los repartidores según su experiencia?
7. ¿Qué tipos de cocina son más populares en diferentes zonas geográficas?
8. ¿Cómo varían los montos de pedidos según la temporada o días festivos?

## Implementación con Hadoop

El esquema está implementado utilizando MapReduce en Hadoop, con clases Java dedicadas para generar cada tabla de dimensión y la tabla de hechos a partir de los datos fuente en MySQL. Estas clases extraen, transforman y cargan los datos al data warehouse.
