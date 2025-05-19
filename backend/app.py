#!/usr/bin/env python3
# SecureScout - Backend Application Entry Point

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
# Use local config module instead of importing
try:
    from backend.config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    if os.environ.get('SECURESCOUT_ENV') == 'production':
        from backend.config import ProductionConfig
        app.config.from_object(ProductionConfig)
except ImportError as e:
    logger.error(f"Error importing config: {e}")
    # Basic config for demo
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'demo-key'

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'environment': os.environ.get('SECURESCOUT_ENV', 'development')
    })

# Import and register API endpoints
try:
    from api.scan_controller import scan_bp
    from api.report_controller import report_bp
    from api.config_controller import config_bp
    
    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(config_bp, url_prefix='/api/config')
except ImportError as e:
    logger.error(f"Error importing blueprints: {e}")
    
    # Simplified endpoint for demo
    @app.route('/api/demo', methods=['GET'])
    def demo():
        return jsonify({
            'status': 'Demo mode',
            'message': 'SecureScout backend is running in demo mode'
        })

# Removed register blueprint statements since they're now in the try block

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting SecureScout backend service...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8001)), debug=True)