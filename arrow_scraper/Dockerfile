# ArrowTuner API Backend Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for runtime files and user data directory for persistent storage
RUN mkdir -p /app/data/processed /app/data/raw /app/user_data

# Set proper permissions
RUN chmod +x /app/api.py /app/database_import_manager.py /app/start-api-robust.sh /app/start-api.sh

# Create non-root user with specific UID/GID for consistency
RUN addgroup --gid 1000 appgroup && \
    adduser --disabled-password --gecos '' --uid 1000 --gid 1000 appuser

# Import arrow database from JSON files using modern import system
RUN echo "🏹 Building arrow database from JSON files..." && \
    python database_import_manager.py --import-all --force && \
    echo "Database import completed, checking result:" && \
    ls -la arrow_database.db && \
    python -c "import sqlite3; conn=sqlite3.connect('arrow_database.db'); print('Arrow count:', conn.execute('SELECT COUNT(*) FROM arrows').fetchone()[0]); conn.close()" && \
    echo "Copying database to backup location:" && \
    cp arrow_database.db /app/arrow_database_backup.db && \
    echo "Final database verification:" && \
    ls -la /app/arrow*.db && \
    echo "Setting ownership and permissions..." && \
    chown -R appuser:appgroup /app && \
    chmod 664 /app/arrow*.db && \
    chmod 775 /app/user_data && \
    echo "Final file check after ownership change:" && \
    ls -la /app/arrow*.db && \
    ls -la /app/user_data/

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Expose port
EXPOSE 5000

# Run the application with enhanced database initialization
CMD ["./start-api-robust.sh"]