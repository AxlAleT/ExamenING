FROM mysql:8

# Set MySQL environment variables
ENV MYSQL_ROOT_PASSWORD=example
ENV MYSQL_DATABASE=ordersdb
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=password

# Configure MySQL to allow LOAD DATA INFILE
COPY ./my.cnf /etc/mysql/conf.d/my.cnf

# Add healthcheck to verify the database is running
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD mysqladmin ping -h localhost -u root --password=$MYSQL_ROOT_PASSWORD || exit 1

# Copy initialization files
COPY db.sql /docker-entrypoint-initdb.d/
COPY utils-python/unnormalized.csv /docker-entrypoint-initdb.d/

# Fix CSV file permissions
RUN chmod 644 /docker-entrypoint-initdb.d/unnormalized.csv && \
    chown mysql:mysql /docker-entrypoint-initdb.d/unnormalized.csv

# Expose MySQL port
EXPOSE 3306

# Create a volume for data persistence
VOLUME /var/lib/mysql
