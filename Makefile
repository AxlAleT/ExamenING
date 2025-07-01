# Makefile for Data Warehouse ETL System Docker Operations

.PHONY: help build up down logs shell test clean backup restore

# Default target
help:
	@echo "Available commands:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start development environment"
	@echo "  up-prod    - Start production environment"
	@echo "  down       - Stop all services"
	@echo "  down-prod  - Stop production services"
	@echo "  logs       - Show logs for all services"
	@echo "  logs-web   - Show web service logs"
	@echo "  shell      - Open shell in web container"
	@echo "  shell-db   - Open MySQL shell"
	@echo "  test       - Run tests"
	@echo "  test-etl   - Run ETL tests with sample data"
	@echo "  migrate    - Run database migrations"
	@echo "  clean      - Clean up Docker resources"
	@echo "  backup     - Backup databases"
	@echo "  restore    - Restore databases from backup"
	@echo "  health     - Check application health"

# Build images
build:
	docker-compose build

build-prod:
	docker-compose -f docker-compose.prod.yml build

# Start services
up:
	docker-compose up -d

up-prod:
	docker-compose -f docker-compose.prod.yml up -d

# Stop services
down:
	docker-compose down

down-prod:
	docker-compose -f docker-compose.prod.yml down

# Show logs
logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-prod:
	docker-compose -f docker-compose.prod.yml logs -f

# Shell access
shell:
	docker-compose exec web bash

shell-db:
	docker-compose exec mysql_db mysql -u root -p

shell-redis:
	docker-compose exec redis redis-cli

# Database operations
migrate:
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py migrate --database=olapdb

migrate-prod:
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --database=olapdb

# Testing
test:
	docker-compose exec web python manage.py test

test-etl:
	docker-compose exec web python manage.py test_etl --sample

test-etl-prod:
	docker-compose -f docker-compose.prod.yml exec web python manage.py test_etl --sample

# ETL operations
run-etl:
	docker-compose exec web python manage.py run_warehouse_etl --stats

run-etl-prod:
	docker-compose -f docker-compose.prod.yml exec web python manage.py run_warehouse_etl --stats

# Health check
health:
	docker-compose exec web python health_check.py

health-prod:
	docker-compose -f docker-compose.prod.yml exec web python health_check.py

# Backup operations
backup:
	@echo "Creating database backups..."
	@mkdir -p backups
	docker-compose exec -T mysql_db mysqldump -u root -pexample ordersdb > backups/ordersdb_$$(date +%Y%m%d_%H%M%S).sql
	docker-compose exec -T mysql_db mysqldump -u root -pexample olapdb > backups/olapdb_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup completed!"

backup-prod:
	@echo "Creating production database backups..."
	@mkdir -p backups
	docker-compose -f docker-compose.prod.yml exec -T mysql_db mysqldump -u root -p$$DB_PASSWORD ordersdb > backups/ordersdb_prod_$$(date +%Y%m%d_%H%M%S).sql
	docker-compose -f docker-compose.prod.yml exec -T mysql_db mysqldump -u root -p$$DB_PASSWORD olapdb > backups/olapdb_prod_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Production backup completed!"

# Restore operations (specify BACKUP_FILE=filename)
restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Usage: make restore BACKUP_FILE=backups/ordersdb_20240101_120000.sql"; \
		exit 1; \
	fi
	docker-compose exec -T mysql_db mysql -u root -pexample ordersdb < $(BACKUP_FILE)

# Cleanup operations
clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

clean-all:
	docker-compose down -v --rmi all
	docker system prune -a -f
	docker volume prune -f

# Reset everything
reset: clean up migrate
	@echo "Environment reset completed!"

reset-prod: clean build-prod up-prod migrate-prod
	@echo "Production environment reset completed!"

# Development helpers
dev-setup: build up migrate
	@echo "Development environment is ready!"
	@echo "Access the application at: http://localhost:8000"
	@echo "Default admin credentials: admin/admin123"

prod-setup: build-prod up-prod migrate-prod
	@echo "Production environment is ready!"
	@echo "Access the application at: http://localhost"

# Monitoring
stats:
	docker stats

ps:
	docker-compose ps

ps-prod:
	docker-compose -f docker-compose.prod.yml ps

# Update operations
update:
	git pull
	docker-compose down
	docker-compose build
	docker-compose up -d
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py migrate --database=olapdb

update-prod:
	git pull
	docker-compose -f docker-compose.prod.yml down
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --database=olapdb
