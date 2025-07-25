# Arrow Tuning Platform - Production Deployment

This directory contains all scripts and configurations needed to deploy the Arrow Tuning Platform to a production Ubuntu server.

## Quick Start

1. **Server Setup** (run on fresh Ubuntu 20.04+ server):
```bash
sudo ./scripts/server-setup.sh
```

2. **Application Deployment**:
```bash
./scripts/deploy.sh
```

3. **Start Services**:
```bash
sudo systemctl start arrowtuner
sudo systemctl enable arrowtuner
```

## Directory Structure

```
deploy/
├── scripts/           # Deployment and maintenance scripts
├── config/           # Production configuration files
├── systemd/          # Systemd service files
├── nginx/            # Nginx configuration
├── backup/           # Backup scripts and configs
└── monitoring/       # Health check and monitoring scripts
```

## Production Requirements

- Ubuntu 20.04+ LTS server
- Minimum 2GB RAM, 20GB storage
- Python 3.8+
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

## Security Features

- Nginx reverse proxy with rate limiting
- Systemd service isolation
- Environment variable security
- Database backups
- Log rotation
- Health monitoring

## Maintenance

- **Update application**: `./scripts/update.sh`
- **Backup database**: `./scripts/backup.sh`
- **Check health**: `./scripts/health-check.sh`
- **View logs**: `./scripts/logs.sh`