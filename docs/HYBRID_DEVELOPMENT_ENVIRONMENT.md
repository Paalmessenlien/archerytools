# Hybrid Development Environment

**⚠️ DEPRECATED (August 2025)**: This hybrid development approach has been superseded by the unified startup system. Please use `./start-unified.sh dev start` for new development.

**📚 Legacy Documentation**: This document is maintained for historical reference and understanding of the hybrid development architecture that was used before the unified system.

**🚀 Single-Command Development Environment Solution**

This document describes the hybrid development environment that eliminates native binding issues while maintaining production compatibility.

## Overview

The hybrid development environment combines the best of both worlds:
- **API Container**: Runs in Docker with production-identical schema
- **Frontend Host**: Runs natively on host system avoiding native binding issues

## Quick Start

### Single Command Startup
```bash
./start-hybrid-dev.sh start
```

### Available Commands
```bash
./start-hybrid-dev.sh start     # Start complete development environment
./start-hybrid-dev.sh stop      # Stop all services
./start-hybrid-dev.sh restart   # Restart all services
./start-hybrid-dev.sh status    # Check service health
./start-hybrid-dev.sh logs      # View service logs
./start-hybrid-dev.sh api-shell # Open shell in API container
./start-hybrid-dev.sh help      # Show help message
```

## Architecture

### API Container (Docker)
- **Environment**: Production Docker container
- **Database**: SQLite with production-identical schema
- **Migrations**: Automatic database migrations on startup
- **Port**: http://localhost:5000
- **Health**: http://localhost:5000/api/health

### Frontend Host (Native)
- **Environment**: Host Node.js environment
- **Dependencies**: Native npm installation
- **Port**: http://localhost:3000
- **Hot Reload**: Full Nuxt 3 development features

## Benefits

### ✅ Solves Critical Issues
- **No oxc-parser Problems**: Frontend runs natively avoiding native binding compilation
- **Schema Consistency**: API uses identical production database structure
- **Database Permissions**: Automatic database initialization with proper container user permissions (August 2025)
- **Migration Compatibility**: Fixed migration system to handle schema changes gracefully (August 2025)
- **Development Features**: Hot reload, debugging, live development preserved
- **Easy Setup**: Single command startup with automatic dependency management

### ✅ Production Compatibility
- **Same Migrations**: Uses identical database migration system
- **Same Schema**: Database structure matches production exactly
- **Same Environment**: API container mirrors production deployment
- **Zero Conflicts**: No schema mismatches between development and production

## Prerequisites

### Required Software
- **Docker & Docker Compose**: For API container
- **Node.js 18+**: For frontend development
- **npm**: For package management

### Environment Setup
1. **Environment File**: `.env` file with required configuration
2. **Frontend Dependencies**: Automatically installed by startup script
3. **Docker Network**: Automatically created for API container

## Service Management

### Automatic Setup
The startup script automatically handles:
- ✅ **Dependency Verification**: Checks Docker, Node.js, npm availability
- ✅ **Environment Validation**: Verifies .env configuration
- ✅ **Frontend Setup**: Installs dependencies if needed
- ✅ **Service Orchestration**: Starts API container and frontend host
- ✅ **Health Monitoring**: Waits for services to be ready
- ✅ **Process Management**: Tracks PIDs and handles cleanup

### Health Checks
- **API Health**: Validates API container responds to health endpoint
- **Frontend Health**: Ensures frontend responds to HTTP requests
- **Process Tracking**: Monitors frontend process with PID file
- **Graceful Shutdown**: Handles interrupts and cleanup properly

## Service Status

### Check Service Health
```bash
./start-hybrid-dev.sh status
```

**Example Output:**
```
📊 Service Status:
=================
✅ API Container: Running
✅ API Health: OK
✅ Frontend Process: Running (PID: 12345)
✅ Frontend Health: OK

🌐 Access URLs (if services are running):
   Frontend:  http://localhost:3000
   API:       http://localhost:5000/api/health
   Admin:     http://localhost:3000/admin
```

## Development Workflow

### 1. Start Development Environment
```bash
./start-hybrid-dev.sh start
```

### 2. Develop with Hot Reload
- **Frontend Changes**: Automatically reloaded via Nuxt 3 dev server
- **API Changes**: Automatically reloaded via Docker volume mount
- **Database Changes**: Use migration system for schema updates

### 3. Access Development URLs
- **Main Application**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API Health**: http://localhost:5000/api/health
- **API Documentation**: See [API_ENDPOINTS.md](API_ENDPOINTS.md)

### 4. Debug Services
```bash
# Open shell in API container
./start-hybrid-dev.sh api-shell

# View service logs
./start-hybrid-dev.sh logs

# Check service status
./start-hybrid-dev.sh status
```

### 5. Stop Development Environment
```bash
./start-hybrid-dev.sh stop
```

## Troubleshooting

### Common Issues

#### Frontend Fails to Start
**Symptoms**: Frontend health check fails
**Solutions**:
1. Check Node.js version: `node --version` (requires 18+)
2. Clear dependencies: `rm -rf frontend/node_modules frontend/.nuxt`
3. Restart services: `./start-hybrid-dev.sh restart`

#### API Container Issues
**Symptoms**: API health check fails
**Solutions**:
1. Check Docker status: `docker ps`
2. View API logs: `docker-compose -f docker-compose.dev.yml logs api`
3. Restart container: `./start-hybrid-dev.sh restart`

#### Database Permission Issues (Fixed August 2025)
**Symptoms**: "unable to open database file" errors
**Root Cause**: Container user permissions on Docker volume
**Solution**: 
- **Automatically resolved** in current version through:
  - Enhanced Dockerfile.dev with proper user permissions
  - Automatic database initialization in start-hybrid-dev.sh
  - Docker volume setup with correct ownership
- **Manual fix if needed**: Rebuild container with `docker-compose -f docker-compose.dev.yml build api`

#### Migration System Errors (Fixed August 2025)  
**Symptoms**: "no such column: bs.draw_length" migration errors
**Root Cause**: Migration attempting to query dropped columns
**Solution**:
- **Automatically resolved** through enhanced migration logic
- Migration now checks column existence before queries
- **Manual verification**: Run migration test in container:
  ```bash
  ./start-hybrid-dev.sh api-shell
  python3 -c "from user_database import UserDatabase; UserDatabase().migrate_draw_length_to_users()"
  ```

#### Port Conflicts
**Symptoms**: Services fail to bind to ports
**Solutions**:
1. Kill conflicting processes: `pkill -f "nuxt dev"`
2. Stop existing containers: `docker-compose -f docker-compose.dev.yml down`
3. Use status command to identify conflicts: `./start-hybrid-dev.sh status`

#### Environment Issues
**Symptoms**: Missing .env file or configuration
**Solutions**:
1. Copy example: `cp .env.example .env`
2. Edit configuration: Configure Google OAuth, API keys
3. Restart services: `./start-hybrid-dev.sh restart`

### Advanced Troubleshooting

#### Manual Service Management
If the startup script fails, you can start services manually:

**Start API Container:**
```bash
docker-compose -f docker-compose.dev.yml up -d api
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

#### Debug API Container
```bash
# Open interactive shell
./start-hybrid-dev.sh api-shell

# Or manually:
docker-compose -f docker-compose.dev.yml exec api /bin/bash
```

#### Check Frontend Process
```bash
# Check if frontend is running
ps aux | grep "nuxt dev"

# Check frontend PID file
cat .frontend.pid
```

## Migration from Other Development Methods

### From Legacy Docker Development
1. Stop existing containers: `docker-compose down`
2. Start hybrid environment: `./start-hybrid-dev.sh start`
3. No additional configuration needed

### From Manual Development
1. Stop manual services (Ctrl+C in terminals)
2. Start hybrid environment: `./start-hybrid-dev.sh start`
3. Environment automatically configured

### From Full Docker Development
1. Stop Docker services: `./start-docker-dev.sh stop`
2. Start hybrid environment: `./start-hybrid-dev.sh start`
3. Maintains same database and configuration

## Technical Details

### Process Management
- **Frontend PID**: Stored in `.frontend.pid` file
- **Signal Handling**: SIGINT and SIGTERM handled gracefully
- **Cleanup**: Automatic process cleanup on script exit
- **Background Execution**: Frontend runs in background with output redirection

### Health Checking
- **API Readiness**: Polls `/api/simple-health` endpoint
- **Frontend Readiness**: Polls root path for 200 response
- **Timeout Handling**: 30s for API, 60s for frontend
- **Retry Logic**: 1-second intervals with failure detection

### Network Configuration
- **API Container**: Runs on Docker network `arrowtuner-dev-network`
- **Frontend Host**: Runs on host network, connects to localhost:5000
- **Port Mapping**: 5000 (API), 3000 (Frontend)
- **Cross-Origin**: Configured via Nuxt proxy settings

## Integration with Existing Tools

### Compatible with Existing Scripts
- **Production Deployment**: `./start-unified.sh ssl domain.com`
- **Legacy Development**: `./start-local-dev.sh start`
- **Docker Development**: `./start-docker-dev.sh start`

### Database Compatibility
- **Same Migrations**: Uses identical migration system as production
- **Same Schema**: Database structure matches production exactly
- **Same Data**: Can import/export data to production systems

### IDE Integration
- **VS Code**: Works with existing workspace configuration
- **Hot Reload**: Both API and frontend support live editing
- **Debugging**: Supports breakpoints and debugging tools

## Advanced Configuration

### Environment Variables
Key environment variables for hybrid development:
```bash
# API Configuration
SECRET_KEY=your-secret-key
DEEPSEEK_API_KEY=your-deepseek-api-key
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend Configuration  
NUXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NUXT_PUBLIC_API_BASE=http://localhost:5000/api
NODE_ENV=development
```

### Custom Ports
To use different ports, modify the script variables:
- Edit `start-hybrid-dev.sh`
- Update `API_COMPOSE_FILE` and port checks
- Modify health check URLs accordingly

### Additional Services
To add services (like nginx proxy):
1. Modify `docker-compose.dev.yml`
2. Update startup script service management
3. Add health checks for new services

## Performance Optimization

### Frontend Performance
- **Native Node.js**: No Docker overhead for frontend
- **Hot Module Replacement**: Faster development builds
- **Native Dependencies**: All native bindings work correctly

### API Performance
- **Container Reuse**: Docker container stays running
- **Volume Mounts**: Fast file changes via bind mounts
- **Health Caching**: Efficient health check implementation

### Startup Performance
- **Dependency Caching**: Reuses installed frontend dependencies
- **Parallel Startup**: API and frontend start concurrently
- **Fast Health Checks**: Optimized health check intervals

## Security Considerations

### Development Security
- **Local Only**: Services bound to localhost only
- **No Production Data**: Uses development database
- **Environment Isolation**: API runs in container isolation

### Access Control
- **Admin Access**: Automatic admin privileges for configured email
- **API Authentication**: JWT token authentication system
- **Frontend Security**: CORS configured for development

## Conclusion

The hybrid development environment provides the optimal balance of:
- **Reliability**: Production-identical API environment
- **Performance**: Native frontend execution
- **Simplicity**: Single-command operation
- **Compatibility**: Works with existing tooling

This approach eliminates the complex native binding issues while maintaining full development capabilities and production compatibility.

For additional documentation, see:
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - General development information
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database structure details
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - API endpoint documentation