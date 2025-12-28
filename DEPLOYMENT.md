# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 3000, 8000, 5432, 6379 available

## Quick Start

### 1. Clone and Setup

```bash
cd SmartHabbit
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache/broker
- FastAPI backend
- Celery worker
- Celery beat scheduler
- React frontend

### 3. Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

Or create initial migration:

```bash
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
docker-compose exec backend alembic upgrade head
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_USER=smarthabit
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=smarthabit_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email (Optional - for nudges)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@smarthabit.com

# Application
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Migrations

### Create Migration

```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Apply Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### Rollback Migration

```bash
docker-compose exec backend alembic downgrade -1
```

## Production Deployment

### 1. Update Docker Compose

For production, use a production-ready setup:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    environment:
      ENVIRONMENT=production
    # ... rest of config
```

### 2. Use Production WSGI Server

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install gunicorn uvicorn[standard]

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. Add Nginx Reverse Proxy

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 4. SSL/TLS Setup

Use Let's Encrypt with Certbot:

```bash
certbot --nginx -d your-domain.com
```

### 5. Environment Variables

Set production environment variables:
- Strong `SECRET_KEY`
- Production database credentials
- Redis credentials
- Email SMTP settings
- CORS origins (your domain)

### 6. Database Backups

Set up automated backups:

```bash
# Backup script
docker-compose exec postgres pg_dump -U smarthabit smarthabit_db > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U smarthabit smarthabit_db < backup.sql
```

## Monitoring

### Health Checks

All services have health checks configured. Check status:

```bash
docker-compose ps
```

### Logs

View logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Celery Monitoring

Install Flower for Celery monitoring:

```yaml
# Add to docker-compose.yml
flower:
  build:
    context: ./backend
  command: celery -A celery_app.celery_app flower --port=5555
  ports:
    - "5555:5555"
  environment:
    CELERY_BROKER_URL: redis://redis:6379/0
```

Access at: http://localhost:5555

## Scaling

### Horizontal Scaling

1. **Backend**: Run multiple FastAPI instances behind load balancer
2. **Celery Workers**: Add more worker containers
3. **Database**: Use read replicas for read-heavy operations
4. **Redis**: Use Redis Cluster for high availability

### Vertical Scaling

Increase resources in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U smarthabit smarthabit_db
```

### Redis Connection Issues

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

### WebSocket Issues

- Ensure WebSocket endpoint uses `ws://` or `wss://` in production
- Check CORS settings
- Verify JWT token is valid
- Check backend logs for connection errors

### Celery Tasks Not Running

```bash
# Check worker logs
docker-compose logs celery_worker

# Check beat logs
docker-compose logs celery_beat

# Manually trigger task
docker-compose exec backend python -c "from celery_app.tasks import detect_habit_risks; detect_habit_risks.delay()"
```

## Development Setup

### Local Development (Without Docker)

1. **Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **Frontend**:
```bash
cd frontend
npm install
npm run dev
```

3. **PostgreSQL & Redis**: Run via Docker or local installation

### Hot Reload

Both frontend and backend support hot reload in development mode.

## CI/CD Pipeline (Example)

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Your deployment commands
```

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs for suspicious activity
- [ ] Rate limiting (add if needed)
- [ ] Input validation (already implemented)

## Performance Tuning

1. **Database Indexes**: Already added on frequently queried fields
2. **Connection Pooling**: Configured in SQLAlchemy
3. **Caching**: Redis caching for expensive queries
4. **Async Operations**: All I/O operations are async
5. **Background Jobs**: Heavy operations moved to Celery

## Backup Strategy

1. **Database**: Daily automated backups
2. **Redis**: Persistence enabled (AOF)
3. **Application Code**: Version control (Git)
4. **User Data**: Regular exports (implement if needed)

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review documentation
3. Check GitHub issues
4. Contact support team

