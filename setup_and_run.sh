#!/bin/bash

# This script checks the OS and helps with Docker installation if needed

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
    echo "Detected OS: $OS $VERSION"
else
    echo "Cannot detect OS. Please install Docker manually."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Would you like to install it? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        case $OS in
            fedora)
                echo "Installing Docker on Fedora..."
                sudo dnf -y install dnf-plugins-core
                sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
                sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo usermod -aG docker $USER
                echo "Docker installed successfully. You may need to log out and log back in to use Docker without sudo."
                ;;
            ubuntu|debian)
                echo "Installing Docker on $OS..."
                sudo apt-get update
                sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
                curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                sudo apt-get update
                sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                sudo usermod -aG docker $USER
                echo "Docker installed successfully. You may need to log out and log back in to use Docker without sudo."
                ;;
            *)
                echo "Unsupported OS: $OS. Please install Docker manually."
                exit 1
                ;;
        esac
    else
        echo "Docker installation skipped. Please install Docker manually."
        exit 1
    fi
else
    echo "Docker is already installed."
fi

# Check if Docker Compose is installed
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "docker-compose is already installed."
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "Docker Compose plugin is already installed."
else
    echo "Docker Compose is not installed. Would you like to install it? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        case $OS in
            fedora)
                echo "Installing Docker Compose on Fedora..."
                sudo dnf install -y docker-compose-plugin
                DOCKER_COMPOSE_CMD="docker compose"
                ;;
            ubuntu|debian)
                echo "Installing Docker Compose on $OS..."
                sudo apt-get install -y docker-compose-plugin
                DOCKER_COMPOSE_CMD="docker compose"
                ;;
            *)
                echo "Unsupported OS: $OS. Please install Docker Compose manually."
                exit 1
                ;;
        esac
    else
        echo "Docker Compose installation skipped. Please install Docker Compose manually."
        exit 1
    fi
fi

echo "Docker and Docker Compose are ready to use."
echo "Running the Hadoop ETL job..."
./run_hadoop_job.sh
