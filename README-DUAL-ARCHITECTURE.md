# ArrowTuner - Modern Arrow Tuning Platform

Professional arrow selection and tuning calculator with modern Material Design 3 UI.

## 🎯 Platform Overview

ArrowTuner is a comprehensive arrow database and tuning calculator that provides professional archery equipment recommendations. The platform features a modern dual architecture with Material Web Components, dark mode support, and advanced filtering capabilities.

**Latest Updates (2025):**
- ✨ **Material Design 3** UI with dark mode support
- 🔧 **Enhanced filtering** with diameter ranges and manufacturer sorting
- 📱 **Responsive design** optimized for all devices
- 🚀 **Performance improvements** with SSR optimization
- 🎨 **Professional styling** with comprehensive button fix solutions

## 🏗️ Architecture

The ArrowTuner platform uses a modern dual architecture:

- **Frontend**: Nuxt 3 (Vue.js) SPA with Material Web Components
- **Backend**: Flask API-only server with RESTful endpoints  
- **Database**: SQLite with 197+ arrow specifications from 13 manufacturers
- **UI Framework**: Tailwind CSS + Material Design 3 theming
- **State Management**: Pinia stores for reactive bow configuration
- **Dark Mode**: Complete theme system with user preference persistence

## Quick Start

### 1. Install Dependencies

**Backend Dependencies:**
```bash
cd arrow_scraper
pip install -r requirements.txt
```

**Frontend Dependencies:**
```bash
cd frontend
npm install
```

### 2. Start the Application

**Option A: Using the startup script (Recommended)**
```bash
./scripts/start-dual-architecture.sh start
```

**Option B: Manual startup**
```bash
# Terminal 1 - API Backend
cd arrow_scraper
python api.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:5000
- **API Health**: http://localhost:5000/api/health

## API Endpoints

### Core Endpoints

- `GET /api/health` - System health check
- `GET /api/arrows` - Get arrows with filtering
- `GET /api/arrows/:id` - Get specific arrow details
- `GET /api/manufacturers` - Get all manufacturers
- `POST /api/tuning/calculate-spine` - Calculate recommended spine
- `POST /api/tuning/recommendations` - Get arrow recommendations
- `POST /api/arrows/compatible` - Check arrow compatibility

### Database Endpoints

- `GET /api/database/stats` - Get database statistics

### Session Endpoints

- `POST /api/tuning/sessions` - Create tuning session
- `GET /api/tuning/sessions` - Get all sessions
- `GET /api/tuning/sessions/:id` - Get specific session

## Frontend Architecture

### Pages
- `/` - Bow configuration and setup
- `/recommendations` - Personalized arrow recommendations
- `/database` - Complete arrow database browser

### Components
- `CompatibleArrowsList.vue` - Shows compatible arrows for current bow config
- Default layout with navigation and responsive design

### State Management
The application uses Pinia for state management with the `useBowConfigStore`:

```javascript
const bowConfigStore = useBowConfigStore()

// Reactive bow configuration
const bowConfig = computed(() => bowConfigStore.bowConfig)

// Update configuration
bowConfigStore.updateBowConfig({ draw_weight: 45 })

// Get recommendations
const recommendations = await bowConfigStore.loadRecommendations()
```

## Development

### Environment Setup

Create `.env` file in the root directory:
```env
# API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SECRET_KEY=your-secret-key-here
API_PORT=5000

# Frontend Configuration
FRONTEND_PORT=3000
NODE_ENV=development
API_BASE_URL=http://localhost:5000
```

### Development Commands

```bash
# Start both services in development mode
NODE_ENV=development ./scripts/start-dual-architecture.sh start

# Frontend development with hot reload
cd frontend && npm run dev

# API development with debug mode
cd arrow_scraper && FLASK_DEBUG=true python api.py
```

## Production Deployment

### Docker Deployment (Recommended)

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Production Deployment

```bash
# Start production services
NODE_ENV=production ./scripts/start-dual-architecture.sh start

# Or start individually
# API: gunicorn --bind 0.0.0.0:5000 --workers 4 arrow_scraper.api:app
# Frontend: cd frontend && npm run build && npm run preview
```

## Architecture Benefits

1. **Modern Frontend**: Vue.js 3 with Composition API and TypeScript support
2. **API-First Design**: RESTful API that can support multiple clients
3. **Better Performance**: SPA with client-side routing and caching
4. **Enhanced UX**: Reactive state management and real-time updates
5. **Scalability**: Independent scaling of frontend and backend services
6. **Development Experience**: Hot reload, TypeScript, and modern tooling

## Migration Notes

- The original Flask web application (`webapp.py`) is still available but deprecated
- All data and calculations remain the same - only the presentation layer changed
- The API endpoints maintain compatibility with existing data structures
- Session storage is currently in-memory (consider Redis for production)

## API Documentation

For complete API documentation, see the interactive documentation at `/api/docs` (when implemented) or refer to the API endpoint definitions in `arrow_scraper/api.py`.