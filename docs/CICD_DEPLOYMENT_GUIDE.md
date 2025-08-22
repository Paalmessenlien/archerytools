# Professional CI/CD Setup for Archery Tools

## Overview

This guide provides a comprehensive plan for implementing professional CI/CD pipelines for the Archery Tools platform using GitHub Actions. The setup enables automatic deployments from development to staging to production with proper safety measures, database management, and rollback capabilities.

## Architecture Overview

### Environment Strategy
- **Development**: Local development environment (existing)
- **Stage Environment**: Automatic deployment from `stage` branch (ports 3001/5001)
- **Production Environment**: Automatic deployment from `production` branch (ports 80/443)
- **Deployment Flow**: `development` → `stage` → `production`

### Key Features
- Zero-downtime blue-green deployments
- Automatic rollbacks on failure
- Environment-specific databases with backup automation
- Health checks and monitoring
- Branch protection and approval gates
- SSL certificate automation

## Recommended Solution: GitHub Actions + Docker

### Why GitHub Actions?
- **Seamless Integration**: Works perfectly with your existing Docker infrastructure
- **Cost Effective**: Free for public repositories, affordable for private
- **Professional Grade**: Enterprise-level features and reliability
- **Perfect Fit**: Ideal for your two-branch workflow (stage → production)
- **Existing Infrastructure**: Leverages your `start-unified.sh` script

### Alternative Solutions Considered
1. **Jenkins**: More complex setup, requires dedicated server resources
2. **GitLab CI/CD**: Good option but requires GitLab migration  
3. **Drone CI**: Lightweight but less ecosystem support
4. **Azure DevOps**: Microsoft-focused, overkill for current setup
5. **Local Git Hooks**: Simple but not scalable or reliable

## Implementation Plan

### Phase 1: Repository Setup

#### 1.1 Create Branch Structure
```bash
# Create staging branch from main
git checkout main
git checkout -b stage
git push origin stage

# Create production branch from main  
git checkout main
git checkout -b production
git push origin production
```

#### 1.2 Set Up Branch Protection Rules
In GitHub repository settings:
- **Stage Branch Protection**:
  - Require pull request reviews before merging
  - Require status checks to pass before merging
  - Include administrators in restrictions

- **Production Branch Protection**:
  - Require pull request reviews before merging
  - Require status checks to pass before merging
  - Restrict pushes to specific people/teams
  - Include administrators in restrictions

#### 1.3 Configure Auto-Merge Flow
- Stage successful deployments automatically create PRs to production
- Production merges require manual approval or auto-merge on all checks passing

### Phase 2: Environment Configuration

#### 2.1 Create Environment-Specific Configurations

**Create directory structure:**
```
environments/
├── stage/
│   ├── .env
│   └── docker-compose.stage.yml
└── production/
    ├── .env
    └── docker-compose.production.yml
```

**Stage Environment (`environments/stage/.env`):**
```bash
# Stage Environment Configuration
DEPLOYMENT_MODE=stage
DOMAIN_NAME=stage.yourdomain.com
SSL_ENABLED=false

# Ports (different from production)
API_PORT=5001
FRONTEND_PORT=3001

# Flask Configuration
FLASK_ENV=staging
SECRET_KEY=stage-secret-key-here

# Database Paths
ARROW_DATABASE_PATH=/app/databases/stage/arrow_database.db
USER_DATABASE_PATH=/app/databases/stage/arrow_database.db

# Google OAuth (stage app)
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-stage-google-client-id
GOOGLE_CLIENT_SECRET=your-stage-google-client-secret
GOOGLE_REDIRECT_URI=http://stage.yourdomain.com:3001
```

**Production Environment (`environments/production/.env`):**
```bash
# Production Environment Configuration
DEPLOYMENT_MODE=production
DOMAIN_NAME=yourdomain.com
SSL_ENABLED=true

# Ports (standard)
API_PORT=5000
FRONTEND_PORT=3000

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=production-secret-key-here

# Database Paths
ARROW_DATABASE_PATH=/app/databases/production/arrow_database.db
USER_DATABASE_PATH=/app/databases/production/arrow_database.db

# Google OAuth (production app)
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-production-google-client-id
GOOGLE_CLIENT_SECRET=your-production-google-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com
```

#### 2.2 Enhance start-unified.sh for Environment Support

**Add environment parameter support:**
```bash
# Usage examples:
./start-unified.sh stage deploy          # Deploy stage environment
./start-unified.sh production deploy     # Deploy production environment
./start-unified.sh stage stop           # Stop stage environment
./start-unified.sh production stop      # Stop production environment
```

### Phase 3: GitHub Actions Workflows

#### 3.1 Stage Deployment Workflow

**File: `.github/workflows/deploy-stage.yml`**
```yaml
name: Deploy to Stage

on:
  push:
    branches: [ stage ]
  pull_request:
    branches: [ stage ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          cd arrow_scraper
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          cd arrow_scraper
          python -m pytest tests/ || python test_basic.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/stage'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Deploy to Stage
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/archerytools
            git fetch origin
            git checkout stage
            git pull origin stage
            
            # Copy stage environment
            cp environments/stage/.env .env
            
            # Create stage database directory
            mkdir -p databases/stage
            
            # Stop existing stage deployment
            ./start-unified.sh stage stop || true
            
            # Start stage deployment
            ./start-unified.sh stage deploy
            
            # Wait for services to be ready
            sleep 30
            
            # Health check
            curl -f http://localhost:3001/api/health || exit 1
            
      - name: Run Integration Tests
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/archerytools
            # Run integration tests against stage
            curl -f http://localhost:3001/api/health
            # Add more comprehensive tests here
            
      - name: Notify Success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "Stage deployment successful! 🚀"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
          
      - name: Create Production PR
        if: success()
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          base: production
          head: stage
          title: "Auto-deploy to production from successful stage"
          body: |
            This PR was automatically created after successful stage deployment.
            
            **Stage Deployment Details:**
            - Commit: ${{ github.sha }}
            - Tests: ✅ Passed
            - Integration Tests: ✅ Passed
            - Health Check: ✅ Passed
```

#### 3.2 Production Deployment Workflow

**File: `.github/workflows/deploy-production.yml`**
```yaml
name: Deploy to Production

on:
  push:
    branches: [ production ]
  workflow_dispatch:
    inputs:
      skip_backup:
        description: 'Skip database backup (not recommended)'
        required: false
        default: 'false'

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Create Database Backup
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/archerytools
            
            # Create backup with timestamp
            timestamp=$(date +"%Y%m%d_%H%M%S")
            backup_name="production_pre_deploy_${timestamp}"
            
            # Use existing backup system
            ./backup-unified.sh --name "$backup_name"
            
            # Verify backup
            ls -la backups/ | tail -5

  deploy:
    needs: backup
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Blue-Green Deployment
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/archerytools
            git fetch origin
            git checkout production
            git pull origin production
            
            # Copy production environment
            cp environments/production/.env .env
            
            # Create production database directory
            mkdir -p databases/production
            
            # Blue-Green Deployment Strategy
            echo "Starting blue-green deployment..."
            
            # Deploy to green environment (temp ports)
            export API_PORT=5002
            export FRONTEND_PORT=3002
            ./start-unified.sh production deploy
            
            # Wait for green environment
            sleep 60
            
            # Health check on green
            if curl -f http://localhost:3002/api/health; then
              echo "Green environment healthy, switching traffic..."
              
              # Stop blue environment
              ./start-unified.sh production stop || true
              
              # Switch to production ports
              export API_PORT=5000
              export FRONTEND_PORT=3000
              ./start-unified.sh ssl ${{ secrets.DOMAIN_NAME }}
              
              # Final health check
              sleep 30
              if curl -f https://${{ secrets.DOMAIN_NAME }}/api/health; then
                echo "Production deployment successful!"
              else
                echo "Production health check failed, rolling back..."
                exit 1
              fi
            else
              echo "Green environment failed health check, aborting deployment"
              exit 1
            fi
            
      - name: Smoke Tests
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            # Run production smoke tests
            curl -f https://${{ secrets.DOMAIN_NAME }}/api/health
            curl -f https://${{ secrets.DOMAIN_NAME }}/api/arrows/count
            # Add more smoke tests here
            
      - name: Notify Success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "Production deployment successful! 🎉"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
          
  rollback:
    needs: [backup, deploy]
    runs-on: ubuntu-latest
    if: failure()
    
    steps:
      - name: Automatic Rollback
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/archerytools
            echo "Deployment failed, initiating rollback..."
            
            # Stop failed deployment
            ./start-unified.sh production stop || true
            
            # Find latest backup
            latest_backup=$(ls -t backups/production_pre_deploy_*.tar.gz | head -1)
            
            if [ -n "$latest_backup" ]; then
              echo "Rolling back to: $latest_backup"
              ./restore-unified.sh --file "$latest_backup" --force
              
              # Restart with previous version
              ./start-unified.sh ssl ${{ secrets.DOMAIN_NAME }}
              
              echo "Rollback completed"
            else
              echo "No backup found for rollback!"
              exit 1
            fi
            
      - name: Notify Rollback
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: "Production deployment failed and was rolled back! 🚨"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Phase 4: Database Management

#### 4.1 Environment-Specific Database Structure
```
databases/
├── stage/
│   ├── arrow_database.db
│   └── backups/
└── production/
    ├── arrow_database.db
    └── backups/
```

#### 4.2 Enhanced Backup System

**Modify backup-unified.sh for environment support:**
```bash
#!/bin/bash
# Enhanced backup script with environment support

ENVIRONMENT=${1:-production}
BACKUP_NAME=${2:-"${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S)"}

echo "Creating backup for $ENVIRONMENT environment..."

# Create environment-specific backup
mkdir -p "backups/$ENVIRONMENT"
cp "databases/$ENVIRONMENT/arrow_database.db" "backups/$ENVIRONMENT/${BACKUP_NAME}.db"
tar -czf "backups/${BACKUP_NAME}.tar.gz" -C "databases/$ENVIRONMENT" .

echo "Backup created: backups/${BACKUP_NAME}.tar.gz"
```

### Phase 5: Monitoring & Safety

#### 5.1 Health Check Endpoints

**Enhance API health checks in `arrow_scraper/api.py`:**
```python
@app.route('/api/health/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check for CI/CD monitoring"""
    try:
        # Database connectivity
        db = UnifiedDatabase()
        arrow_count = db.get_arrow_count()
        db.close()
        
        # Environment info
        environment = os.getenv('DEPLOYMENT_MODE', 'unknown')
        
        return jsonify({
            'status': 'healthy',
            'environment': environment,
            'database': {
                'connected': True,
                'arrow_count': arrow_count
            },
            'timestamp': datetime.utcnow().isoformat(),
            'version': os.getenv('GIT_COMMIT', 'unknown')
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

#### 5.2 Monitoring Dashboard

**Create monitoring script for both environments:**
```bash
#!/bin/bash
# monitor-environments.sh

echo "=== Environment Status ==="

echo "Stage Environment (ports 3001/5001):"
curl -s http://localhost:3001/api/health/detailed | jq '.'

echo -e "\nProduction Environment (ports 80/443):"
curl -s https://yourdomain.com/api/health/detailed | jq '.'

echo -e "\n=== Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Phase 6: Security Features

#### 6.1 GitHub Secrets Configuration

**Required secrets in GitHub repository:**
- `HOST`: Server IP address
- `USERNAME`: SSH username
- `SSH_KEY`: SSH private key for server access
- `DOMAIN_NAME`: Production domain name
- `SLACK_WEBHOOK`: Slack webhook URL for notifications
- `DEEPSEEK_API_KEY`: API key for arrow data processing
- `GOOGLE_CLIENT_SECRET_STAGE`: Stage Google OAuth secret
- `GOOGLE_CLIENT_SECRET_PROD`: Production Google OAuth secret

#### 6.2 SSL Certificate Automation

**Enhance start-unified.sh for SSL automation:**
```bash
setup_ssl_certificates() {
    local domain=$1
    
    if [ ! -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]; then
        echo "Setting up SSL certificates for $domain..."
        
        # Stop nginx temporarily
        docker-compose -f docker-compose.unified.yml stop nginx || true
        
        # Generate certificates
        certbot certonly --standalone -d "$domain" --email "$SSL_EMAIL" --agree-tos --non-interactive
        
        # Restart nginx with SSL
        docker-compose -f docker-compose.unified.yml up -d nginx
    else
        echo "SSL certificates already exist for $domain"
    fi
}
```

## Implementation Steps

### Step 1: Prepare Repository
```bash
# 1. Create branches
git checkout -b stage
git push origin stage
git checkout main
git checkout -b production  
git push origin production

# 2. Create directory structure
mkdir -p environments/stage environments/production
mkdir -p .github/workflows
```

### Step 2: Configure Environments
```bash
# 3. Create environment files
# Copy provided .env templates to environments/stage/ and environments/production/

# 4. Test environment switching
cp environments/stage/.env .env
./start-unified.sh dev start
# Verify stage configuration works
```

### Step 3: Set Up GitHub Actions
```bash
# 5. Add workflow files
# Copy provided workflow YAML files to .github/workflows/

# 6. Configure GitHub secrets
# Add all required secrets in GitHub repository settings
```

### Step 4: Test Deployment Pipeline
```bash
# 7. Test stage deployment
git checkout stage
git add .
git commit -m "Add CI/CD configuration"
git push origin stage
# Watch GitHub Actions run

# 8. Test production deployment
# Create PR from stage to production
# Verify production deployment works
```

### Step 5: Monitor and Refine
```bash
# 9. Set up monitoring
chmod +x monitor-environments.sh
./monitor-environments.sh

# 10. Test rollback procedure
# Simulate deployment failure and verify rollback works
```

## Benefits

### Professional Workflow
- **Automated Testing**: Every push runs tests before deployment
- **Environment Consistency**: Same deployment process for stage and production
- **Branch Protection**: Prevents accidental direct pushes to production
- **Approval Gates**: Human oversight for production deployments

### Safety Features
- **Automatic Backups**: Database backed up before every production deployment
- **Health Checks**: Deployment fails if services aren't healthy
- **Rollback Automation**: Failed deployments automatically revert to previous version
- **Blue-Green Deployment**: Zero-downtime production deployments

### Operational Excellence
- **Monitoring**: Real-time status of both environments
- **Notifications**: Slack alerts for deployment status
- **Logging**: Complete audit trail of all deployments
- **Security**: Encrypted secrets and SSL automation

## Maintenance

### Regular Tasks
- Monitor GitHub Actions usage and costs
- Review and update branch protection rules
- Test rollback procedures monthly
- Update SSL certificates automatically
- Clean up old backup files

### Troubleshooting
- Check GitHub Actions logs for deployment failures
- Verify server connectivity and SSH keys
- Monitor disk space for database and backups
- Review application logs for errors

This CI/CD setup provides enterprise-grade deployment automation while leveraging your existing Docker infrastructure and maintaining the flexibility to customize workflows as needed.