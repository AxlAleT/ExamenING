# Modelado de Datos: Esquema Estrella para Sistema de Delivery

## Introducción

Este documento presenta el modelo de datos en esquema estrella (star schema) diseñado para el sistema de pedidos de comida a domicilio. El esquema se ha optimizado para facilitar el análisis de datos y responder a preguntas de negocio relacionadas con tiempos de entrega, costos, patrones de pedidos y satisfacción del cliente.

## Esquema Estrella

El esquema estrella es una técnica de modelado de datos ampliamente utilizada en data warehousing que facilita las consultas analíticas mediante una estructura intuitiva de tablas de hechos y dimensiones. Este tipo de esquema es ideal para este caso por:

1. **Rendimiento**: Optimiza el tiempo de respuesta para consultas analíticas complejas
2. **Simplicidad**: Estructura fácil de entender y navegar
3. **Flexibilidad**: Permite añadir nuevas dimensiones según evolucionen las necesidades de negocio

## Componentes del Esquema

### Tabla de Hechos: Fact_Pedidos

La tabla de hechos central contiene los eventos transaccionales (pedidos) y sus métricas asociadas:

- **Claves foráneas**: Conectan con todas las dimensiones relevantes
  - customer_id → dim_Cliente
  - restaurant_id → dim_Restaurante
  - delivery_person_id → dim_Repartidor
  - date_id → dim_Tiempo
  - location_id → dim_Ubicación
  - time_slot_id → dim_TimeSlot

- **Métricas de negocio**:
  - monto_pedido: Valor monetario del pedido
  - tiempo_preparacion: Minutos que toma preparar el pedido
  - tiempo_entrega: Minutos de transporte hasta el cliente
  - calificacion: Valoración del servicio (1-5)
  - tiempo_total: Suma de tiempo de preparación y entrega

### Tablas de Dimensiones

#### dim_Cliente
Contiene atributos descriptivos de los clientes:
- Segmentación por tipo de cliente (Premium, Regular, Básico)
- Antigüedad como cliente
- Datos demográficos básicos

#### dim_Restaurante
Describe las características de los restaurantes:
- Tipo de cocina o especialidad
- Capacidad de procesamiento de pedidos
- Ubicación y características operativas

#### dim_Repartidor
Propiedades de los repartidores:
- Experiencia (meses en servicio)
- Zona de operación asignada
- Tipo de vehículo
- Calificación histórica

#### dim_Tiempo
Jerarquía temporal para análisis por diferentes granularidades de tiempo:
- Día de la semana
- Mes y trimestre
- Temporada del año
- Indicadores de fin de semana y festivos

#### dim_Ubicación
Jerarquía geográfica:
- Barrio o vecindario
- Código postal
- Ciudad
- Región

#### dim_TimeSlot
Segmentación del día en franjas horarias:
- Mañana, tarde, noche
- Horas pico y horas valle
- Franjas de comidas principales

## Ventajas del Diseño

1. **Análisis multidimensional**: Permite analizar datos desde múltiples perspectivas (tiempo, ubicación, tipo de cliente, etc.)
2. **Desnormalización estratégica**: Reduce la necesidad de joins complejos en consultas analíticas
3. **Historial temporal**: Facilita el análisis de tendencias y patrones temporales
4. **Jerarquías de agregación**: Permite navegar desde niveles detallados a agregados

## Implementación y ETL

El proceso de ETL (Extracción, Transformación y Carga) se implementa mediante trabajos MapReduce en Hadoop que:

1. Extraen datos de la base de datos operacional MySQL
2. Transforman y enriquecen los datos para el modelo dimensional
3. Cargan los datos en formato optimizado para análisis

## Conclusión

El esquema estrella implementado proporciona una base sólida para el análisis de datos del negocio de delivery de comida, permitiendo identificar oportunidades de mejora en eficiencia operativa, satisfacción del cliente y optimización de costos.
