#!/bin/bash
# Fix Python dependencies issues on Ubuntu servers
# Run as root if you encounter python3-pip installation errors

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

log "Fixing Python dependencies on Ubuntu server..."

# Update package lists
log "Updating package lists..."
apt update

# Check Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "unknown")
log "Ubuntu version: $UBUNTU_VERSION"

# Install Python3 if not present
if ! command -v python3 >/dev/null 2>&1; then
    log "Installing Python3..."
    apt install -y python3
fi

# Check Python version
PYTHON_VERSION=$(python3 --version)
log "Python version: $PYTHON_VERSION"

# Try different methods to install pip
log "Installing pip..."

# Method 1: Standard package manager
if apt install -y python3-pip; then
    log "✅ python3-pip installed successfully via apt"
else
    warn "❌ python3-pip installation via apt failed"
    
    # Method 2: Install via get-pip.py
    log "Trying get-pip.py method..."
    if curl -sSL https://bootstrap.pypa.io/get-pip.py | python3; then
        log "✅ pip installed successfully via get-pip.py"
    else
        warn "❌ get-pip.py method failed"
        
        # Method 3: Try alternative package names
        log "Trying alternative package names..."
        if apt install -y python3-setuptools python3-wheel; then
            log "✅ Installed setuptools and wheel"
            # Try to install pip via setuptools
            python3 -m easy_install pip || warn "easy_install method failed"
        fi
    fi
fi

# Verify pip installation
log "Verifying pip installation..."
if command -v pip3 >/dev/null 2>&1; then
    PIP_VERSION=$(pip3 --version)
    log "✅ pip3 found: $PIP_VERSION"
elif command -v pip >/dev/null 2>&1; then
    PIP_VERSION=$(pip --version)
    log "✅ pip found: $PIP_VERSION"
else
    error "❌ pip installation failed completely"
fi

# Upgrade pip and install essential packages
log "Upgrading pip and installing essential packages..."
if command -v pip3 >/dev/null 2>&1; then
    pip3 install --upgrade pip setuptools wheel
    log "✅ Essential Python packages installed"
elif command -v pip >/dev/null 2>&1; then
    pip install --upgrade pip setuptools wheel
    log "✅ Essential Python packages installed"
fi

# Install other required packages
log "Installing other required system packages..."
apt install -y \
    python3-venv \
    python3-dev \
    build-essential \
    nginx \
    supervisor \
    ufw \
    git \
    curl \
    wget \
    unzip \
    sqlite3

log "✅ Python dependencies fix completed successfully!"
log "You can now run the main server setup script:"
log "sudo ./deploy/scripts/server-setup.sh"