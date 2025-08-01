# ArcheryTool - Professional Archery Tools

**Version:** 2.1.0  
**Status:** Production Ready  
**Architecture:** Modern SPA with API Backend

ArcheryTool is a comprehensive web application that provides professional archery tools including arrow selection, tuning calculations, equipment guides, and component databases. Built with modern web technologies, it offers professional-grade spine calculations, intelligent arrow recommendations, and a comprehensive database of archery equipment specifications.

## 🚀 Latest Updates (August 2025)

### Enhanced Scraping System
- **Pattern Learning**: 46%+ faster scraping with intelligent content extraction
- **Multi-Language Support**: Automatic translation for German, Italian content
- **Flexible Commands**: New `--learn`, `--learn-all`, `--limit` flags
- **Optional API Usage**: Choose between fast mode or DeepSeek extraction

### Database Import System  
- **JSON-First Architecture**: JSON files serve as authoritative data source
- **Automatic Import**: Database updates from JSON files during server startup
- **Smart Detection**: Only imports when JSON files are newer than database
- **Production Ready**: No server-side scraping in production environments

## 🎯 Features

### Core Functionality
- **Professional Spine Calculation** - Industry-standard formulas for accurate spine recommendations
- **Intelligent Arrow Matching** - Advanced recommendation engine with compatibility scoring  
- **Comprehensive Database** - 400+ arrows from 13+ manufacturers with detailed specifications
- **Advanced Filtering** - Search by manufacturer, material, arrow type, spine range, diameter, and more
- **Dark/Light Mode** - Full responsive design with theme support
- **Diameter Categories** - Professional arrow shaft diameter classification system

### Technical Features  
- **Modern Architecture** - Nuxt 3 frontend with Flask API backend
- **Real-time Calculations** - Instant spine and tuning recommendations
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **TypeScript** - Full type safety and developer experience
- **Material Design 3** - Modern UI components with accessibility features
- **Professional Deployment** - Production-ready with Docker support

## 🏗️ Architecture

### Frontend (Nuxt 3)
- **Framework:** Nuxt 3 + Vue.js 3 + TypeScript
- **Styling:** Tailwind CSS + Material Web Components
- **State Management:** Pinia stores
- **Build Tool:** Vite
- **Port:** 3000 (development), 80/443 (production)

### Backend (Flask API)
- **Framework:** Flask + Python 3.8+
- **Database:** SQLite with comprehensive arrow specifications
- **API:** RESTful endpoints with CORS support
- **Intelligence:** DeepSeek API integration for data extraction
- **Port:** 5000 (development), 5000 (production behind proxy)

### Data Layer
- **Arrow Database:** 400+ specifications with spine, diameter, weight data
- **Manufacturers:** 13+ supported manufacturers with live data
- **Categories:** Professional diameter classification system
- **Search:** Advanced filtering with category-based statistics

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+ with pip
- **Git** for version control

### Development Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd arrowtuner2
```

2. **Backend Setup:**
```bash
cd arrow_scraper
pip install -r requirements.txt
python arrow_database.py  # Initialize database
python api.py  # Start API server (port 5000)
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
npm run dev  # Start frontend (port 3000)
```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:5000
   - Health Check: http://localhost:5000/api/health

### Environment Variables

**Backend (.env in arrow_scraper/):**
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SECRET_KEY=your-secret-key-change-in-production
```

**Frontend (.env in frontend/):**
```env
API_BASE_URL=http://localhost:5000/api
```

## 📋 API Endpoints

### Core Endpoints
- `GET /api/health` - System health check
- `GET /api/database/stats` - Database statistics with diameter categories
- `GET /api/arrows` - Arrow search with filtering
- `GET /api/arrows/<id>` - Individual arrow details
- `GET /api/manufacturers` - Available manufacturers
- `GET /api/materials` - Available materials  
- `GET /api/arrow-types` - Available arrow types

### Tuning Endpoints
- `POST /api/tuning/calculate-spine` - Calculate recommended spine
- `POST /api/tuning/recommendations` - Get arrow recommendations
- `POST /api/arrows/compatible` - Find compatible arrows

## 🎯 User Guide

### Bow Setup
1. **Basic Configuration:**
   - Select bow type (Compound, Recurve, Longbow, Traditional)
   - Choose arrow type (Hunting, Target, 3D, etc.)
   - Set draw weight (20-80 lbs)
   - Configure arrow length and material
   - Select point weight

2. **Advanced Setup (Optional):**
   - Arrow rest type (for compound bows)
   - Nock type preferences
   - Vane specifications
   - Number of vanes

3. **Get Recommendations:**
   - System calculates optimal spine
   - Displays compatible arrows with scoring
   - Shows detailed specifications and alternatives

### Database Search
- **Quick Search:** Use the search bar for manufacturer/model names
- **Filter Options:** Manufacturer, Arrow Type, Material
- **Advanced Filters:** Spine range, diameter, GPI weight
- **View Details:** Click any arrow for complete specifications

## 💾 Database

### Arrow Specifications
The system includes comprehensive data for 400+ arrows:
- **Spine Values** - Complete range from ultra-light to heavy
- **Diameter Categories** - Professional classification system:
  - Ultra-thin (.166") - High-end target arrows
  - Thin (.204") - 3D and precision target
  - Small hunting (.244") - Compact hunting diameter  
  - Standard target (.246") - Most common target/hunting
  - Standard hunting (.300") - Popular hunting diameter
  - Large hunting (.340") - Larger game applications
  - Heavy hunting (.400"+) - Traditional and heavy setups

### Manufacturers Supported
- Easton Archery (multiple categories)
- Gold Tip (hunting and target)
- Victory Archery (hunting and target)
- Carbon Express (complete line)
- Nijora Archery (German precision)
- DK Bow (German traditional/modern)
- Plus 7 additional manufacturers

## 🕷️ Arrow Data Scraping

### Quick Start
```bash
cd arrow_scraper
source venv/bin/activate

# Update all manufacturers with translation
python main.py --update-all

# Learn patterns from first URL of each manufacturer
python main.py --learn-all --limit 1

# Update specific manufacturer
python main.py --update-all --manufacturer dkbow

# Fast mode without API calls
python main.py --learn --manufacturer easton --limit 3
```

### Scraping Modes
- **Pattern Learning** (`--learn`): Learns extraction patterns for 46%+ faster scraping
- **Full Update** (`--update-all`): Complete scraping with DeepSeek API
- **Fast Mode**: Use learned patterns without API calls
- **Limited Scraping** (`--limit N`): Process only first N URLs

### Database Import
The system automatically imports JSON data during server startup:
- Scans `data/processed/` for new JSON files
- Compares timestamps with database
- Updates only when JSON files are newer
- No manual database operations needed

### Production Workflow
1. **Local Development**: Run scraper to update JSON files
2. **Commit Changes**: Push JSON files to repository
3. **Deploy**: Server automatically imports on startup
4. **No Server Scraping**: Production never scrapes websites

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # ESLint checking
npm run type-check   # TypeScript checking
```

### Backend Development  
```bash
cd arrow_scraper
python api.py                    # Start API server
python test_setup.py             # Test system setup
python arrow_database.py         # Rebuild database
python migrate_diameter_categories.py  # Database migrations
```

### Testing
```bash
# Frontend
cd frontend && npm run test

# Backend  
cd arrow_scraper && python test_diameter_categories.py
```

## 🏭 Production Deployment

### Enhanced Docker Deployment (Recommended)
```bash
# Standard deployment
docker-compose up -d

# Enhanced deployment with verification
./deploy-enhanced.sh docker-compose.enhanced-ssl.yml

# The enhanced deployment includes:
# - Automatic database import from JSON files
# - Health checks and verification
# - User database persistence
# - Build integrity checking
```

### Database Import on Startup
The server automatically:
1. Checks `data/processed/` for JSON files
2. Compares with existing database
3. Imports new data if needed
4. Logs all operations
5. Continues startup regardless of import status

### Manual Ubuntu Deployment
See `deploy/` directory for comprehensive production scripts:
- `scripts/server-setup.sh` - Ubuntu server initialization
- `scripts/deploy.sh` - Application deployment
- `scripts/health-check.sh` - Monitoring and alerts

### System Requirements
- **CPU:** 2+ cores recommended
- **RAM:** 4GB minimum, 8GB recommended  
- **Storage:** 10GB minimum
- **OS:** Ubuntu 20.04+ or similar Linux distribution

## 🔐 Security Features

- **Input Validation** - All API inputs validated and sanitized
- **CORS Protection** - Properly configured cross-origin policies
- **Rate Limiting** - Protection against abuse
- **SQL Injection Prevention** - Parameterized queries throughout
- **XSS Protection** - Template escaping and CSP headers
- **Environment Secrets** - API keys properly isolated

## 🐛 Troubleshooting

### Common Issues

**Frontend won't start:**
- Check Node.js version (18+ required)
- Run `npm install` to update dependencies
- Verify API_BASE_URL in environment

**API connection errors:**
- Ensure Flask server is running on port 5000  
- Check CORS configuration
- Verify database exists and is accessible

**Dark mode issues:**
- Tailwind config includes `darkMode: 'class'`
- Check browser developer tools for CSS loading

**Database errors:**
- Run `python arrow_database.py` to rebuild
- Check SQLite file permissions
- Verify data files in `data/processed/`

### Performance Tips
- Use browser caching for static assets
- Enable gzip compression on server
- Consider CDN for production deployment
- Monitor API response times

## 📈 Monitoring

### Health Checks
- **Application:** `/api/health` endpoint
- **Database:** Connection and query performance  
- **Frontend:** Bundle size and load times

### Metrics to Monitor
- API response times
- Database query performance
- Frontend bundle size
- User engagement patterns
- Error rates and types

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Follow coding standards (ESLint, Prettier, PEP 8)
4. Add tests for new functionality
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards
- **Frontend:** ESLint + Prettier, TypeScript strict mode
- **Backend:** PEP 8, type hints, comprehensive docstrings
- **Commits:** Conventional commit format
- **Testing:** Unit tests for new features

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Manufacturers** for providing comprehensive arrow specifications
- **DeepSeek AI** for intelligent data extraction capabilities
- **Vue.js & Nuxt** teams for the excellent framework
- **Material Design** team for the component system
- **Archery Community** for domain expertise and feedback

## 📞 Support

For questions, issues, or feature requests:
- **Issues:** GitHub Issues tab
- **Documentation:** See `docs/` directory  
- **API Reference:** `/api/health` for endpoint testing

---

**Built with ❤️ for the archery community**

Ready for beta testing with professional-grade arrow tuning capabilities!