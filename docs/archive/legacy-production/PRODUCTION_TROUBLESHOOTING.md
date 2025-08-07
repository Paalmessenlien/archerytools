# 🚨 Production Troubleshooting Guide

This guide provides solutions for common production issues with the ArrowTuner unified architecture deployment.

## 🔍 Common Production Issues

### **Issue 1: Site Inaccessible (ContainerConfig Error)**

**Symptoms:**
- Website not accessible (e.g., https://archerytool.online/ down)
- Docker Compose shows `ERROR: for arrowtuner-db-init 'ContainerConfig'`
- Services fail to start with container configuration conflicts

**Root Cause:**
- Orphaned containers from previous deployments with conflicting configurations
- Multiple Docker Compose files creating incompatible container setups
- Docker's volume binding conflicts between old and new containers

**Solution:**

```bash
# Step 1: Complete shutdown
docker-compose -f docker-compose.unified.yml down

# Step 2: Clean up orphaned containers and networks
docker container prune -f
docker network prune -f
docker system prune -f

# Step 3: Remove specific conflicting containers
docker ps -a | grep arrowtuner
docker rm -f $(docker ps -a | grep arrowtuner | awk '{print $1}') 2>/dev/null || true

# Step 4: Remove conflicting networks
docker network ls | grep arrowtuner
docker network rm $(docker network ls | grep arrowtuner | awk '{print $1}') 2>/dev/null || true

# Step 5: Start with proper profiles
docker-compose -f docker-compose.unified.yml --profile with-nginx up -d
```

**Alternative: Enhanced Deployment**
```bash
# Use enhanced deployment script (if available)
./deploy-enhanced.sh docker-compose.unified.yml --profile=with-nginx
```

**Emergency Workaround:**
```bash
# Use production override if main approach fails
docker-compose -f docker-compose.unified.yml down
docker container prune -f
docker-compose -f docker-compose.unified.yml -f docker-compose.production-override.yml --profile with-nginx up -d
```

### **Issue 2: Nginx Not Running (No Web Access)**

**Symptoms:**
- Direct API access works (http://server:5000/api/health)
- Frontend works directly (http://server:3000)
- Web domain is inaccessible
- Nginx container not in `docker ps` output

**Root Cause:**
- Nginx service has `profiles: - with-nginx` requiring explicit activation
- Service not started with proper profile flags

**Solution:**

```bash
# Check current running services
docker-compose -f docker-compose.unified.yml ps

# Verify nginx is NOT running
docker-compose -f docker-compose.unified.yml ps nginx

# Start with nginx profile
docker-compose -f docker-compose.unified.yml --profile with-nginx up -d

# For SSL production
docker-compose -f docker-compose.unified.yml --profile with-nginx --profile with-backup up -d
```

**Verification:**
```bash
# Check nginx is running
docker-compose -f docker-compose.unified.yml ps nginx

# Test health endpoint
curl -I http://localhost/health
curl -I https://yourdomain.com/health

# Check nginx logs
docker-compose -f docker-compose.unified.yml logs nginx --tail=20
```

### **Issue 3: SSL Certificate Problems**

**Symptoms:**
- HTTP works but HTTPS fails
- Browser shows "Certificate not valid" errors
- Nginx logs show SSL certificate errors

**Root Cause:**
- Missing or expired SSL certificates
- Certificates not properly mounted in Docker container
- Incorrect certificate paths

**Solution:**

```bash
# Check if certificates exist
ls -la deploy/ssl/
ls -la /etc/letsencrypt/live/yourdomain.com/

# Check certificate expiration
openssl x509 -in deploy/ssl/cert.pem -text -noout | grep "Not After"

# Regenerate certificates if needed
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to docker location
sudo mkdir -p deploy/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deploy/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deploy/ssl/key.pem
sudo chown -R $USER:$USER deploy/ssl

# Restart with SSL
docker-compose -f docker-compose.unified.yml --profile with-nginx --profile with-backup up -d
```

### **Issue 4: Database Backup Service Failing**

**Symptoms:**
- `arrowtuner-db-backup exited with code 2`
- Backup service continuously restarting and failing

**Root Cause:**
- Backup service misconfiguration
- Missing backup directories or permissions
- Database not accessible to backup service

**Solution:**

```bash
# Check backup service logs
docker-compose -f docker-compose.unified.yml logs db-backup --tail=20

# Verify backup directories exist
docker-compose -f docker-compose.unified.yml exec api ls -la /app/backups/

# Create backup directory if missing
docker-compose -f docker-compose.unified.yml exec api mkdir -p /app/backups

# Fix permissions
docker-compose -f docker-compose.unified.yml exec api chmod 755 /app/backups

# Restart backup service
docker-compose -f docker-compose.unified.yml restart db-backup
```

### **Issue 5: Health Check Failures**

**Symptoms:**
- Containers showing as "unhealthy" in `docker ps`
- Nginx health check errors: `open() "/usr/share/nginx/html/health" failed`
- Services marked as unhealthy but actually functional

**Root Cause:**
- Health check endpoints not properly configured
- Extended startup times exceeding health check timeouts
- Services not fully ready when health checks run

**Solution:**

```bash
# Check health status
docker-compose -f docker-compose.unified.yml ps

# Test health endpoints manually
curl -f http://localhost:5000/api/health  # API health
curl -f http://localhost:3000/           # Frontend health  
curl -f http://localhost/health          # Nginx health

# Increase health check timeouts if needed (edit docker-compose.unified.yml)
# start_period: 120s  # Allow more time for startup
# interval: 60s       # Check less frequently
# timeout: 30s        # Allow longer response time

# Restart services with longer startup period
docker-compose -f docker-compose.unified.yml restart
```

## 🛠️ Production Maintenance Commands

### **Status Checking**
```bash
# Check all service status
docker-compose -f docker-compose.unified.yml ps

# Check logs for specific service
docker-compose -f docker-compose.unified.yml logs api --tail=50
docker-compose -f docker-compose.unified.yml logs frontend --tail=50
docker-compose -f docker-compose.unified.yml logs nginx --tail=50

# Check system resources
docker stats

# Check disk usage
df -h
docker system df
```

### **Service Management**
```bash
# Restart specific service
docker-compose -f docker-compose.unified.yml restart api
docker-compose -f docker-compose.unified.yml restart frontend
docker-compose -f docker-compose.unified.yml restart nginx

# Stop all services
docker-compose -f docker-compose.unified.yml down

# Start with full production setup
docker-compose -f docker-compose.unified.yml --profile with-nginx --profile with-backup up -d

# Force rebuild if code changed
docker-compose -f docker-compose.unified.yml --profile with-nginx up -d --build
```

### **Database Operations**
```bash
# Access database directly
docker-compose -f docker-compose.unified.yml exec api sqlite3 /app/arrow_database.db

# Create manual backup
docker-compose -f docker-compose.unified.yml exec api python3 /app/backup_manager.py backup

# Check database integrity
docker-compose -f docker-compose.unified.yml exec api python3 /app/database_cleaner.py --database /app/arrow_database.db --validate
```

## 🚀 Production Deployment Checklist

### **Pre-Deployment**
- [ ] Pull latest code: `git pull`
- [ ] Verify environment variables in `.env`
- [ ] Check SSL certificates are valid and accessible
- [ ] Backup current databases
- [ ] Test deployment in staging if available

### **Deployment Steps**
```bash
# 1. Stop current services
docker-compose -f docker-compose.unified.yml down

# 2. Clean up if needed
docker container prune -f
docker network prune -f

# 3. Pull latest images/rebuild
docker-compose -f docker-compose.unified.yml pull
docker-compose -f docker-compose.unified.yml build

# 4. Start services
docker-compose -f docker-compose.unified.yml --profile with-nginx --profile with-backup up -d

# 5. Verify deployment
docker-compose -f docker-compose.unified.yml ps
curl -I https://yourdomain.com/health
```

### **Post-Deployment Verification**
- [ ] All containers show "Up (healthy)" status
- [ ] Website accessible via HTTPS
- [ ] Health endpoints responding: `/health`, `/api/health`
- [ ] User authentication working (Google OAuth)
- [ ] Database operations functional
- [ ] Backup service running without errors

## ⚠️ Emergency Procedures

### **Site Down Emergency**
```bash
# 1. Quick status check
docker-compose -f docker-compose.unified.yml ps
curl -I https://yourdomain.com/

# 2. Check if it's just nginx
curl -I http://server-ip:3000/  # Test frontend direct
curl -I http://server-ip:5000/api/health  # Test API direct

# 3. Emergency restart
docker-compose -f docker-compose.unified.yml restart

# 4. Nuclear option (if site critically down)
docker-compose -f docker-compose.unified.yml down
docker system prune -f
docker-compose -f docker-compose.unified.yml --profile with-nginx up -d --build
```

### **Database Corruption Emergency**
```bash
# 1. Stop services
docker-compose -f docker-compose.unified.yml stop

# 2. Restore from backup
./restore-databases.sh --list
./restore-databases.sh --file latest_backup.tar.gz

# 3. Restart services
docker-compose -f docker-compose.unified.yml start
```

### **SSL Certificate Emergency**
```bash
# 1. Temporary HTTP-only mode
docker-compose -f docker-compose.unified.yml down
# Edit docker-compose.unified.yml to comment out SSL sections
docker-compose -f docker-compose.unified.yml --profile with-nginx up -d

# 2. Fix certificates
sudo certbot certonly --standalone -d yourdomain.com
# Copy certificates as shown in SSL solution above

# 3. Re-enable HTTPS
# Uncomment SSL sections in docker-compose.unified.yml
docker-compose -f docker-compose.unified.yml --profile with-nginx up -d
```

## 📊 Monitoring & Alerting

### **Log Monitoring**
```bash
# Monitor all logs in real-time
docker-compose -f docker-compose.unified.yml logs -f

# Monitor specific service
docker-compose -f docker-compose.unified.yml logs -f nginx

# Search for errors
docker-compose -f docker-compose.unified.yml logs | grep -i error
docker-compose -f docker-compose.unified.yml logs | grep -i fail
```

### **Health Monitoring Script**
Create a monitoring script `health-monitor.sh`:
```bash
#!/bin/bash
# Simple health monitoring for production

echo "=== ArrowTuner Production Health Check ==="
echo "Date: $(date)"

# Check container status
echo -e "\n🐳 Container Status:"
docker-compose -f docker-compose.unified.yml ps

# Check website
echo -e "\n🌐 Website Health:"
if curl -f -s https://yourdomain.com/health > /dev/null; then
    echo "✅ Website: OK"
else
    echo "❌ Website: FAILED"
fi

# Check API
echo -e "\n🔌 API Health:"
if curl -f -s https://yourdomain.com/api/health > /dev/null; then
    echo "✅ API: OK"
else
    echo "❌ API: FAILED"
fi

# Check disk space
echo -e "\n💾 Disk Usage:"
df -h / | tail -1

# Check memory
echo -e "\n🧠 Memory Usage:"
free -h | grep Mem

echo -e "\n=== Health Check Complete ==="
```

## 🔗 Related Documentation

- [UNIFIED_MIGRATION_GUIDE.md](UNIFIED_MIGRATION_GUIDE.md) - Migration from old setup
- [DATABASE_CLEANER_GUIDE.md](DATABASE_CLEANER_GUIDE.md) - Database maintenance
- [DATABASE_PERSISTENCE.md](DATABASE_PERSISTENCE.md) - Backup and restore procedures
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Docker deployment specifics
- [CLAUDE.md](CLAUDE.md) - Complete project documentation

## 🆘 Getting Help

When reporting production issues, include:

1. **Current Status**: Output of `docker-compose -f docker-compose.unified.yml ps`
2. **Error Logs**: Relevant log entries from affected services
3. **Environment**: Production domain, SSL status, deployment method used
4. **Steps Taken**: What troubleshooting steps you've already tried
5. **Timeline**: When the issue started, any recent changes made

**Remember**: Always try `--dry-run` modes for database operations and take backups before making changes in production! 🛡️