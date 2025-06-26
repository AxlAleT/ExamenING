FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AIRFLOW_HOME=/opt/airflow

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create airflow user
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

# Create working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN pip install -e .

# Create necessary directories
RUN mkdir -p data/raw data/processed logs
RUN chmod -R 777 data logs

# Set permissions for airflow
RUN mkdir -p ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/logs
RUN cp dags/* ${AIRFLOW_HOME}/dags/
RUN chown -R airflow: ${AIRFLOW_HOME}

# Switch to airflow user
USER airflow
WORKDIR ${AIRFLOW_HOME}

# Initialize airflow database
RUN airflow db init

# Create admin user
RUN airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Expose port for airflow webserver
EXPOSE 8080

# Create entrypoint script
USER root
RUN echo '#!/bin/bash\n\
if [ "$1" = "webserver" ]; then\n\
    exec airflow webserver\n\
elif [ "$1" = "scheduler" ]; then\n\
    exec airflow scheduler\n\
elif [ "$1" = "etl" ]; then\n\
    cd /app && python -m src.main\n\
elif [ "$1" = "shell" ]; then\n\
    exec /bin/bash\n\
else\n\
    exec "$@"\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

USER airflow
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]
