#!/usr/bin/env python3
"""
Simple test API to check if Flask and CORS are working
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

# Create Flask app
app = Flask(__name__)

# Enable CORS for all domains on all routes
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'Test API is working'
    })

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Hello from test API!',
        'arrows_count': 172
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting test API on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )