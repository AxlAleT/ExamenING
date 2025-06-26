FROM apache/airflow:2.10.2-python3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to root for system installations
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    python3-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory for ETL code
WORKDIR /app

# Copy requirements and install dependencies
COPY --chown=airflow:root requirements.txt .

# Switch to airflow user for pip installations
USER airflow
RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry-core

# Now install your main requirements.txt
# Note: avoid installing airflow again as it's already in the base image
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with proper ownership
USER root
COPY --chown=airflow:root . .

# Copy DAGs to the Airflow DAGs folder
RUN mkdir -p /opt/airflow/dags
RUN cp -r dags/* /opt/airflow/dags/
RUN chown -R airflow: /opt/airflow /app

# Switch back to airflow user to install the package in editable mode
USER airflow
WORKDIR /app
RUN pip install -e .

# Switch back to airflow user for running the container
USER airflow
WORKDIR /opt/airflow

# Expose port for airflow webserver
EXPOSE 8080

# Copy and set up the custom entrypoint script
USER root
COPY --chown=airflow:root ./custom-entrypoint.sh /app/custom-entrypoint.sh
RUN chmod +x /app/custom-entrypoint.sh

USER airflow
WORKDIR /opt/airflow
ENTRYPOINT ["/app/custom-entrypoint.sh"]
CMD ["webserver"]