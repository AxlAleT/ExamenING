# Docker Deployment Guide

This guide explains how to deploy the Data Warehouse ETL System using Docker and Docker Compose.

## Prerequisites

- Docker 20.10 or later
- Docker Compose 2.0 or later
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start (Development)

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd dataWarehouse
   ```

2. **Start the development environment**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Web interface: http://localhost:8000
   - Default admin credentials: admin/admin123
   - MySQL: localhost:3307 (root/example)
   - Redis: localhost:6379

## Production Deployment

1. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

2. **Generate a secure secret key**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Update environment variables**
   ```bash
   # Edit .env file
   SECRET_KEY=your-generated-secret-key
   DB_PASSWORD=your-secure-database-password
   ALLOWED_HOSTS=your-domain.com,your-ip-address
   DEBUG=0
   ```

4. **Deploy with production compose file**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

## Environment Variables

### Required Variables
- `SECRET_KEY`: Django secret key (generate a secure one)
- `DB_PASSWORD`: MySQL root password
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Optional Variables
- `DEBUG`: Set to 0 for production (default: 1)
- `DB_HOST`: Database host (default: mysql_db)
- `DB_PORT`: Database port (default: 3306)
- `REDIS_URL`: Redis connection URL (default: redis://redis:6379/0)

## Services

### Development Environment (docker-compose.yml)
- **mysql_db**: MySQL 8.0 database server
- **redis**: Redis cache and message broker
- **web**: Django application server
- **celery_worker**: Background task worker
- **celery_beat**: Scheduled task scheduler

### Production Environment (docker-compose.prod.yml)
- **mysql_db**: MySQL 8.0 database server
- **redis**: Redis cache and message broker
- **nginx**: Reverse proxy and static file server
- **web**: Django application with Gunicorn
- **celery_worker**: Background task worker
- **celery_beat**: Scheduled task scheduler

## Data Persistence

### Development
- `db_data`: MySQL data
- `redis_data`: Redis data
- `./media`: Uploaded files (bind mount)
- `./logs`: Application logs (bind mount)

### Production
- `db_data_prod`: MySQL data
- `redis_data_prod`: Redis data
- `static_volume`: Static files
- `media_volume`: Uploaded files
- `./logs`: Application logs (bind mount)

## Common Operations

### Start services
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Stop services
```bash
# Development
docker-compose down

# Production
docker-compose -f docker-compose.prod.yml down
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web

# Production
docker-compose -f docker-compose.prod.yml logs -f web
```

### Run Django commands
```bash
# Development
docker-compose exec web python manage.py <command>

# Production
docker-compose -f docker-compose.prod.yml exec web python manage.py <command>
```

### Run ETL commands
```bash
# Test ETL with sample data
docker-compose exec web python manage.py test_etl --sample

# Run warehouse ETL
docker-compose exec web python manage.py run_warehouse_etl --stats

# Process CSV file
docker-compose exec web python manage.py test_etl --file /app/media/your-file.csv
```

### Database operations
```bash
# Run migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py migrate --database=olapdb

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access MySQL shell
docker-compose exec mysql_db mysql -u root -p
```

### Backup and restore
```bash
# Backup database
docker-compose exec mysql_db mysqldump -u root -p ordersdb > backup_ordersdb.sql
docker-compose exec mysql_db mysqldump -u root -p olapdb > backup_olapdb.sql

# Restore database
docker-compose exec -T mysql_db mysql -u root -p ordersdb < backup_ordersdb.sql
docker-compose exec -T mysql_db mysql -u root -p olapdb < backup_olapdb.sql
```

## Scaling

### Scale Celery workers
```bash
# Development
docker-compose up --scale celery_worker=3

# Production
docker-compose -f docker-compose.prod.yml up --scale celery_worker=3 -d
```

### Scale web instances (production with load balancer)
```bash
docker-compose -f docker-compose.prod.yml up --scale web=3 -d
```

## Monitoring

### Health checks
```bash
# Check container health
docker-compose ps

# Web application health
curl http://localhost/health/

# Database health
docker-compose exec mysql_db mysqladmin ping -u root -p
```

### Resource usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Change ports in docker-compose.yml if needed
   ```

2. **Permission issues**
   ```bash
   # Fix permissions for bind mounts
   sudo chown -R $USER:$USER ./media ./logs
   ```

3. **Database connection issues**
   ```bash
   # Check database logs
   docker-compose logs mysql_db
   
   # Ensure database is healthy
   docker-compose exec mysql_db mysqladmin ping -u root -p
   ```

4. **Memory issues**
   ```bash
   # Check available memory
   free -h
   
   # Restart services if needed
   docker-compose restart
   ```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

## Security Considerations

### Production Security
1. Change default passwords
2. Use strong SECRET_KEY
3. Set DEBUG=0
4. Configure proper ALLOWED_HOSTS
5. Use HTTPS (configure SSL certificates)
6. Regular security updates
7. Monitor logs for suspicious activity

### Network Security
- Services communicate through internal Docker network
- Only necessary ports are exposed
- Nginx acts as reverse proxy
- Database is not directly accessible from outside

## Performance Optimization

### Database
- Regular backups
- Monitor query performance
- Consider read replicas for heavy read workloads

### Application
- Monitor Celery task performance
- Scale workers based on load
- Use Redis for caching
- Regular log rotation

### Infrastructure
- Monitor disk space
- Use SSD storage for better performance
- Adequate RAM allocation
- Regular Docker cleanup

## Backup Strategy

### Automated Backups
```bash
# Add to crontab for daily backups
0 2 * * * cd /path/to/project && docker-compose exec -T mysql_db mysqldump -u root -p${DB_PASSWORD} ordersdb > backups/ordersdb_$(date +%Y%m%d).sql
0 2 * * * cd /path/to/project && docker-compose exec -T mysql_db mysqldump -u root -p${DB_PASSWORD} olapdb > backups/olapdb_$(date +%Y%m%d).sql
```

### File Backups
```bash
# Backup uploaded files
tar -czf media_backup_$(date +%Y%m%d).tar.gz ./media/
```

## Updates and Maintenance

### Application Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Run any new migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py migrate --database=olapdb
```

### System Maintenance
```bash
# Clean up unused Docker resources
docker system prune -a

# Update base images
docker-compose pull
docker-compose up --build -d
```
