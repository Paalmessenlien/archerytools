# Docker Deployment Guide for ArrowTuner

## Quick Start

### Prerequisites
- Docker 20.10+ 
- Docker Compose 2.0+
- Domain pointed to your server (for production)

### Environment Setup

1. **Create environment file**:
```bash
# Copy the example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

2. **Required environment variables**:
```env
# API Configuration
SECRET_KEY=your-strong-secret-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# Domain Configuration (for production)
DOMAIN_NAME=archerytool.online
SSL_EMAIL=admin@archerytool.online

# Database Configuration
DATABASE_PATH=/app/data/arrow_database.db
```

## Development Deployment

### Start Development Environment
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Services Available
- **Frontend**: http://localhost:3000 (Nuxt 3 SPA)
- **API**: http://localhost:5000 (Flask API)
- **Nginx**: http://localhost:80 (Reverse proxy)

### Development Commands
```bash
# Rebuild specific service
docker-compose build frontend
docker-compose up -d frontend

# View service logs
docker-compose logs -f api
docker-compose logs -f frontend

# Execute commands in containers
docker-compose exec api python arrow_database.py
docker-compose exec frontend npm run lint

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Production Deployment

### 1. Server Setup
```bash
# Clone repository
git clone https://github.com/Paalmessenlien/archerytools.git
cd archerytools

# Configure environment for production
cp .env.example .env
nano .env  # Add your production values
```

### 2. SSL Certificate Setup
```bash
# Install certbot (if not using Docker SSL)
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone \
  -d archerytool.online \
  -d www.archerytool.online \
  --email admin@archerytool.online \
  --agree-tos
```

### 3. Production Deployment
```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check deployment
curl https://archerytool.online/api/health
```

## Service Architecture

### Frontend (Nuxt 3)
- **Image**: Node.js 20 Alpine
- **Port**: 3000
- **Features**: 
  - Modern Vue.js SPA
  - Tailwind CSS styling  
  - Dark/light mode toggle
  - Professional UI components

### Backend (Flask API)
- **Image**: Python 3.11 Alpine
- **Port**: 5000
- **Features**:
  - RESTful API endpoints
  - Arrow database with 400+ specifications
  - Professional tuning calculations
  - CORS configured for frontend

### Nginx (Reverse Proxy)
- **Image**: Nginx Alpine
- **Ports**: 80, 443
- **Features**:
  - SSL termination
  - Rate limiting
  - Static file serving
  - Health checks

## Docker Images

### Frontend Dependencies Fixed
- **Node.js Version**: Upgraded from 18 to 20 (required for Nuxt 3.17+)
- **Build Process**: Multi-stage build for optimization
- **Dependencies**: Includes dev dependencies for build, production runtime only

### Key Features
- ✅ **Multi-stage builds** for optimized image sizes
- ✅ **Health checks** for all services
- ✅ **Non-root users** for security
- ✅ **Volume persistence** for database and logs
- ✅ **Network isolation** with custom bridge network
- ✅ **Automatic restarts** on failure

## Troubleshooting

### Node.js Version Issues
The error you encountered was due to Nuxt 3.17+ requiring Node.js 20+:
```
npm warn EBADENGINE Unsupported engine {
  package: 'nuxt@3.17.7',
  required: { node: '^20.9.0 || >=22.0.0' },
  current: { node: 'v18.20.8' }
}
```

**Fixed by upgrading Docker images from Node 18 to Node 20.**

### Common Issues

1. **Port conflicts**:
```bash
# Check if ports are in use
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :5000

# Stop conflicting services
docker-compose down
```

2. **Database not found**:
```bash
# Initialize database
docker-compose exec api python arrow_database.py

# Check database status
docker-compose exec api python -c "
import sqlite3
conn = sqlite3.connect('arrow_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM arrows')
print(f'Total arrows: {cursor.fetchone()[0]}')
"
```

3. **SSL certificate issues**:
```bash
# Check certificate
openssl x509 -in /etc/letsencrypt/live/archerytool.online/fullchain.pem -text -noout

# Renew certificate
sudo certbot renew
```

## Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f api
docker-compose logs -f nginx
```

### Database Operations
```bash
# Check database stats
docker-compose exec api curl http://localhost:5000/api/database/stats

# Backup database
docker-compose exec api cp arrow_database.db /app/data/backup-$(date +%Y%m%d).db

# Rebuild database
docker-compose exec api python arrow_database.py
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Remove old images
docker image prune -f
```

## Performance Optimization

### Resource Limits
Add to docker-compose.yml:
```yaml
services:
  frontend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
  api:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"
```

### Monitoring
```bash
# Resource usage
docker stats

# Service health
docker-compose ps
curl http://localhost:5000/api/health
curl http://localhost:3000
```

## Production Checklist

- ✅ Environment variables configured
- ✅ SSL certificates installed
- ✅ Domain DNS pointed to server
- ✅ Firewall configured (ports 80, 443)
- ✅ Docker services running
- ✅ Health checks passing
- ✅ Database initialized with arrow data
- ✅ API endpoints responding
- ✅ Frontend loading correctly

**Your ArrowTuner platform is now ready at https://archerytool.online!**