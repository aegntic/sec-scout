#!/usr/bin/env python3
# SecureScout - Scan Controller API

import os
import uuid
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app

# Initialize Blueprint
scan_bp = Blueprint('scan', __name__)
logger = logging.getLogger(__name__)

# Mock database for development (will be replaced with actual DB)
active_scans = {}
scan_history = []

@scan_bp.route('/start', methods=['POST'])
def start_scan():
    """
    Start a new security scan with the specified parameters
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'target_url' not in data:
            return jsonify({'error': 'Target URL is required'}), 400
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Default scan configuration with overrides from request
        scan_config = {
            'id': scan_id,
            'target_url': data['target_url'],
            'scan_type': data.get('scan_type', 'comprehensive'),
            'modules': data.get('modules', ['discovery', 'authentication', 'injection', 'xss', 'csrf']),
            'max_depth': data.get('max_depth', 3),
            'max_pages': data.get('max_pages', 100),
            'threads': min(data.get('threads', current_app.config['DEFAULT_THREAD_COUNT']), 
                           current_app.config['MAX_THREAD_COUNT']),
            'request_delay': data.get('request_delay', current_app.config['DEFAULT_REQUEST_DELAY']),
            'jitter': data.get('jitter', current_app.config['DEFAULT_JITTER']),
            'user_agent_rotation': data.get('user_agent_rotation', 
                                           current_app.config['DEFAULT_USER_AGENT_ROTATION']),
            'ip_rotation': data.get('ip_rotation', current_app.config['DEFAULT_IP_ROTATION']),
            'custom_headers': data.get('custom_headers', {}),
            'custom_cookies': data.get('custom_cookies', {}),
            'authentication': data.get('authentication', None),
            'start_time': datetime.utcnow().isoformat(),
            'status': 'initializing',
            'progress': 0,
            'findings': []
        }
        
        # Store scan information
        active_scans[scan_id] = scan_config
        scan_history.append({
            'id': scan_id,
            'target_url': data['target_url'],
            'scan_type': scan_config['scan_type'],
            'start_time': scan_config['start_time'],
            'status': 'initializing'
        })
        
        # TODO: Queue the actual scan job with Celery
        # For now, just update the status
        active_scans[scan_id]['status'] = 'queued'
        
        logger.info(f"Scan {scan_id} initialized for target {data['target_url']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Scan initiated successfully',
            'scan_id': scan_id,
            'config': scan_config
        }), 201
        
    except Exception as e:
        logger.error(f"Error starting scan: {str(e)}")
        return jsonify({'error': str(e)}), 500


@scan_bp.route('/status/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    """
    Get the current status of a running scan
    """
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
        
    scan_info = active_scans[scan_id]
    
    return jsonify({
        'scan_id': scan_id,
        'status': scan_info['status'],
        'progress': scan_info['progress'],
        'target_url': scan_info['target_url'],
        'start_time': scan_info['start_time'],
        'elapsed_time': get_elapsed_time(scan_info['start_time']),
        'findings_count': len(scan_info['findings'])
    })


@scan_bp.route('/list', methods=['GET'])
def list_scans():
    """
    List all scans (active and historical)
    """
    return jsonify({
        'active_scans': list(active_scans.values()),
        'scan_history': scan_history
    })


@scan_bp.route('/stop/<scan_id>', methods=['POST'])
def stop_scan(scan_id):
    """
    Stop a running scan
    """
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
        
    # TODO: Implement actual scan stopping logic
    active_scans[scan_id]['status'] = 'stopping'
    
    return jsonify({
        'status': 'success',
        'message': f'Scan {scan_id} is being stopped'
    })


@scan_bp.route('/delete/<scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    """
    Delete scan data and results
    """
    if scan_id not in active_scans and not any(s['id'] == scan_id for s in scan_history):
        return jsonify({'error': 'Scan not found'}), 404
        
    # Remove from active scans if present
    if scan_id in active_scans:
        del active_scans[scan_id]
    
    # Remove from history - avoid using global/nonlocal for simplicity
    new_scan_history = [s for s in scan_history if s['id'] != scan_id]
    scan_history.clear()
    scan_history.extend(new_scan_history)
    
    # TODO: Delete associated reports and data files
    
    return jsonify({
        'status': 'success',
        'message': f'Scan {scan_id} deleted successfully'
    })


def get_elapsed_time(start_time_iso):
    """Calculate elapsed time from ISO format start time to now"""
    start_time = datetime.fromisoformat(start_time_iso)
    elapsed = datetime.utcnow() - start_time
    return str(elapsed).split('.')[0]  # Remove microseconds