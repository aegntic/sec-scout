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
# Enable CORS with more secure settings
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins, "supports_credentials": True}})

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
    app.config['JWT_SECRET_KEY'] = 'demo-jwt-key'

# Set workflow results directory
app.config['WORKFLOW_RESULT_DIR'] = os.environ.get('WORKFLOW_RESULT_DIR', '/tmp/securescout_results')
os.makedirs(app.config['WORKFLOW_RESULT_DIR'], exist_ok=True)

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
    from api.auth_controller import auth_bp, init_auth_manager
    from api.workflow_controller import workflow_bp, register_workflow_blueprint

    # Register blueprints
    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(config_bp, url_prefix='/api/config')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Register workflow blueprint
    register_workflow_blueprint(app)
    logger.info("Registered workflow blueprint")

    # Initialize auth manager
    init_auth_manager(app)
    logger.info("Initialized auth manager")
except ImportError as e:
    logger.error(f"Error importing blueprints: {e}")

    # Simplified endpoints for demo
    @app.route('/api/demo', methods=['GET'])
    def demo():
        return jsonify({
            'status': 'Demo mode',
            'message': 'SecureScout backend is running in demo mode'
        })

    @app.route('/api/auth/setup-status', methods=['GET'])
    def setup_status():
        return jsonify({
            'setup_complete': True,
            'admin_count': 1
        })

    @app.route('/api/auth/login', methods=['POST'])
    def demo_login():
        data = request.get_json()
        # Demo mode - accept any credentials
        return jsonify({
            'access_token': 'demo-access-token',
            'refresh_token': 'demo-refresh-token',
            'user': {
                'username': data.get('username', 'admin'),
                'email': 'admin@demo.local',
                'role': 'ADMIN'
            }
        })

    @app.route('/api/workflows', methods=['GET'])
    def get_workflows():
        return jsonify([])

    @app.route('/api/workflows/<workflow_id>', methods=['GET'])
    def get_workflow(workflow_id):
        return jsonify({
            'id': workflow_id,
            'name': f'Demo Workflow {workflow_id}',
            'status': 'completed',
            'created_at': '2025-05-22T12:00:00Z',
            'updated_at': '2025-05-22T12:30:00Z',
            'tasks': []
        })

    @app.route('/api/workflows/<workflow_id>/findings', methods=['GET'])
    def get_workflow_findings(workflow_id):
        return jsonify([])

    @app.route('/api/workflows/<workflow_id>/tasks', methods=['GET'])
    def get_workflow_tasks(workflow_id):
        return jsonify([])

# Removed register blueprint statements since they're now in the try block

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to response."""
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

if __name__ == '__main__':
    logger.info("Starting SecureScout backend service...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8001)), debug=True)