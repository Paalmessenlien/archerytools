#!/usr/bin/env python3
"""
Arrow Tuning System - Web Server Startup Script
Handles server startup with proper error handling and recovery
"""

import os
import sys
import signal
import time
from contextlib import contextmanager

def signal_handler(sig, frame):
    print('\n🛑 Server shutdown requested...')
    print('✅ Arrow Tuning System stopped')
    sys.exit(0)

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

def startup_banner():
    """Display startup banner"""
    print("=" * 60)
    print("🏹 ARROW TUNING SYSTEM - WEB INTERFACE")
    print("=" * 60)
    print("📊 Professional arrow selection and tuning system")
    print("🌐 Phase 3: Complete web interface with database integration")
    print("")

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking system requirements...")
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
    else:
        print("✅ Virtual environment: Active")
    
    # Check database file
    if os.path.exists('arrow_database.db'):
        print("✅ Database: arrow_database.db found")
    else:
        print("⚠️  Warning: arrow_database.db not found")
    
    # Check templates
    if os.path.exists('templates'):
        print("✅ Templates: Directory found")
    else:
        print("❌ Error: templates directory not found")
        return False
    
    # Check static files
    if os.path.exists('static'):
        print("✅ Static files: Directory found")
    else:
        print("⚠️  Warning: static directory not found")
    
    return True

def start_server():
    """Start the Flask development server"""
    try:
        import webapp
        
        print("\n🚀 Starting Flask development server...")
        print("📍 Local access: http://localhost:5000")
        print("🌐 Network access: http://127.0.0.1:5000")
        print("")
        print("🎯 Available endpoints:")
        print("  • Homepage: /")
        print("  • Arrow Database: /arrows")
        print("  • Tuning Wizard: /tuning")
        print("  • About System: /about")
        print("  • API Statistics: /api/stats")
        print("")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 60)
        
        # Configure and start server
        webapp.app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,           # Disable debug to avoid reloader issues
            threaded=False,        # Single-threaded for SQLite compatibility
            use_reloader=False,    # Disable auto-reload
            use_debugger=False     # Disable debugger
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install Flask Jinja2")
        return False
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main startup function"""
    startup_banner()
    
    if not check_requirements():
        print("\n❌ Requirements check failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Start the server
    success = start_server()
    
    if not success:
        print("\n❌ Failed to start server")
        sys.exit(1)

if __name__ == '__main__':
    main()