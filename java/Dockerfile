FROM openjdk:8-jdk

# Install required packages
RUN apt-get update && \
    apt-get install -y wget curl ssh pdsh

# Set environment variables
ENV HADOOP_VERSION=3.3.4
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Download and extract Hadoop
RUN wget https://downloads.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzf hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION $HADOOP_HOME && \
    rm hadoop-$HADOOP_VERSION.tar.gz

# Set up SSH key
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

# Configure Hadoop
RUN mkdir -p $HADOOP_HOME/logs
COPY hadoop-config/*.xml $HADOOP_CONF_DIR/

# Install MySQL connector
RUN wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar -O $HADOOP_HOME/share/hadoop/common/lib/mysql-connector-java-8.0.28.jar

# Copy the application JAR
COPY target/fooddelivery-dw-1.0-SNAPSHOT.jar /app/
COPY target/dependency/*.jar /app/dependency/

# Set working directory
WORKDIR /app

# Entry point script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
