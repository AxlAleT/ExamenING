FROM ubuntu:22.04

# Set environment variables
ENV HADOOP_VERSION=3.3.4
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

# Install Java, SSH, and other dependencies
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk wget curl ssh pdsh maven default-mysql-client && \
    apt-get clean

# Download and extract Hadoop
RUN wget https://downloads.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzf hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION $HADOOP_HOME && \
    rm hadoop-$HADOOP_VERSION.tar.gz

# Set up SSH key (required for Hadoop)
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

# Configure Hadoop
RUN mkdir -p $HADOOP_HOME/logs
COPY hadoop-config/core-site.xml $HADOOP_CONF_DIR/
COPY hadoop-config/hdfs-site.xml $HADOOP_CONF_DIR/
COPY hadoop-config/mapred-site.xml $HADOOP_CONF_DIR/
COPY hadoop-config/yarn-site.xml $HADOOP_CONF_DIR/

# Install MySQL connector
RUN wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar -O $HADOOP_HOME/share/hadoop/common/lib/mysql-connector-java-8.0.28.jar

# Copy source code
WORKDIR /app
COPY src/ /app/src/
COPY pom.xml /app/

# Build the application
RUN mvn clean package dependency:copy-dependencies

# Entry point script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
