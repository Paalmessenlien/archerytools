# ArrowTuner Development Setup Guide

## Quick Setup for Development

### 1. Environment Configuration

Create your local environment files with real API keys:

```bash
# Copy environment templates
cp .env.example .env
cp arrow_scraper/.env.example arrow_scraper/.env

# Edit with your real API keys
nano .env
nano arrow_scraper/.env
```

### 2. Required API Keys

#### DeepSeek API Key (Required)
- **Purpose**: Intelligent arrow data extraction from manufacturer websites
- **Get it from**: https://deepseek.com
- **Add to**: `DEEPSEEK_API_KEY=your-key-here`

#### OpenAI API Key (Optional)
- **Purpose**: Vision OCR testing for complex specification images
- **Get it from**: https://platform.openai.com/api-keys
- **Add to**: `OPENAI_API_KEY=your-key-here`

### 3. Environment File Structure

#### Root `.env` file:
```env
# Development configuration
SECRET_KEY=dev-secret-key
DEEPSEEK_API_KEY=your-deepseek-key-here
OPENAI_API_KEY=your-openai-key-here
NODE_ENV=development
FLASK_ENV=development
API_BASE_URL=http://localhost:5000/api
```

#### Backend `arrow_scraper/.env` file:
```env
# Backend-specific configuration
DEEPSEEK_API_KEY=your-deepseek-key-here
OPENAI_API_KEY=your-openai-key-here
SECRET_KEY=dev-secret-key
FLASK_ENV=development
DATABASE_PATH=arrow_database.db
LOG_LEVEL=DEBUG
```

### 4. Development Workflow

#### Start Backend API:
```bash
cd arrow_scraper
pip install -r requirements.txt
python api.py
# API available at: http://localhost:5000
```

#### Start Frontend:
```bash
cd frontend
npm install
npm run dev
# Frontend available at: http://localhost:3000
```

#### Test API Functionality:
```bash
# Test DeepSeek integration
cd arrow_scraper
python test_deepseek.py

# Test OpenAI vision (if key configured)
python test_openai_vision_ocr.py

# Test database
python test_diameter_categories.py
```

### 5. Features Available with API Keys

#### With DeepSeek API Key:
- ✅ Arrow data scraping from manufacturer websites
- ✅ Intelligent content extraction
- ✅ Database updates with new arrow specifications
- ✅ Manufacturing data research

#### With OpenAI API Key:
- ✅ Vision OCR for complex specification images
- ✅ Advanced image analysis for Carbon Express charts
- ✅ Fallback extraction for vision-based content

#### Without API Keys:
- ✅ Browse existing arrow database (400+ arrows)
- ✅ Professional spine calculations
- ✅ Arrow recommendations
- ✅ Modern UI with dark/light mode
- ✅ Advanced filtering and search
- ❌ New data scraping disabled
- ❌ Vision OCR testing disabled

### 6. Security Best Practices

#### Never Commit API Keys:
```bash
# .env files are already in .gitignore
# Always use environment variables in code
api_key = os.getenv("DEEPSEEK_API_KEY")
```

#### Production Deployment:
```bash
# Use different keys for production
# Set strong SECRET_KEY
# Configure proper domain and SSL
```

### 7. Common Development Tasks

#### Initialize Database:
```bash
cd arrow_scraper
python arrow_database.py
```

#### Update Database with New Categories:
```bash
python migrate_diameter_categories.py
```

#### Test Specific Manufacturer:
```bash
python main.py easton
```

#### Run Comprehensive Tests:
```bash
python test_setup.py
python test_diameter_categories.py
python test_api.py
```

### 8. API Testing

#### Health Check:
```bash
curl http://localhost:5000/api/health
```

#### Database Stats:
```bash
curl http://localhost:5000/api/database/stats
```

#### Search Arrows:
```bash
curl "http://localhost:5000/api/arrows?manufacturer=Easton&limit=5"
```

#### Get Arrow Types:
```bash
curl http://localhost:5000/api/arrow-types
```

### 9. Troubleshooting

#### API Key Issues:
```bash
# Check environment loading
python -c "import os; print('DeepSeek:', bool(os.getenv('DEEPSEEK_API_KEY')))"
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

#### Database Issues:
```bash
# Check database exists
ls -la arrow_scraper/arrow_database.db

# Rebuild if needed
cd arrow_scraper && python arrow_database.py
```

#### Frontend Issues:
```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules .nuxt
npm install
npm run dev
```

### 10. Production Deployment

When ready for production:

```bash
# Use production deployment scripts
sudo ./deploy/server-setup.sh
sudo ./deploy/deploy.sh yourdomain.com admin@yourdomain.com

# Environment will be automatically configured
# Update /var/www/arrowtuner/arrow_scraper/.env with production keys
```

---

## 🔑 API Key Summary

- **DeepSeek**: Required for data scraping, optional for pure database browsing
- **OpenAI**: Optional, only for advanced vision OCR testing
- **Both keys**: Full functionality including data collection and vision analysis
- **No keys**: Core features still work with existing database

**Ready to start developing! 🏹**