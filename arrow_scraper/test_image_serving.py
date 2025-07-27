#!/usr/bin/env python3
"""
Test script for image serving functionality
"""

from flask import Flask, send_from_directory, jsonify
from pathlib import Path

app = Flask(__name__)

@app.route('/test-image/<path:filename>')
def test_serve_image(filename):
    """Test image serving"""
    try:
        images_dir = Path(__file__).parent / 'data' / 'images'
        print(f"Looking for image: {filename} in {images_dir}")
        
        # Check if file exists
        file_path = images_dir / filename
        print(f"Full path: {file_path}")
        print(f"File exists: {file_path.exists()}")
        
        if not file_path.exists():
            return jsonify({'error': f'Image not found: {filename}'}), 404
        
        # Serve the file
        if filename.endswith('.svg'):
            return send_from_directory(images_dir, filename, mimetype='image/svg+xml')
        else:
            return send_from_directory(images_dir, filename)
            
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error serving image: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting test image server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)