#!/usr/bin/env python3
# SecureScout - Configuration Controller API

import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app

# Initialize Blueprint
config_bp = Blueprint('config', __name__)
logger = logging.getLogger(__name__)

# Default testing profiles
DEFAULT_PROFILES = {
    'passive': {
        'name': 'Passive Scan',
        'description': 'Non-intrusive information gathering only',
        'modules': ['discovery', 'passive_vulnerability', 'ssl_tls', 'headers', 'cookies'],
        'max_depth': 2,
        'max_pages': 100,
        'threads': 5,
        'request_delay': 1.0,
        'jitter': 0.5,
        'user_agent_rotation': True,
        'ip_rotation': False,
        'stealth_level': 'high'
    },
    'standard': {
        'name': 'Standard Scan',
        'description': 'Balanced security testing with moderate intrusiveness',
        'modules': ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 
                   'headers', 'cookies', 'sensitive_data'],
        'max_depth': 3,
        'max_pages': 200,
        'threads': 10,
        'request_delay': 0.5,
        'jitter': 0.2,
        'user_agent_rotation': True,
        'ip_rotation': False,
        'stealth_level': 'medium'
    },
    'aggressive': {
        'name': 'Aggressive Scan',
        'description': 'Comprehensive security testing with high intrusiveness',
        'modules': ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 
                   'headers', 'cookies', 'sensitive_data', 'brute_force', 'dos_simulation', 
                   'file_inclusion', 'command_injection', 'deserialization'],
        'max_depth': 5,
        'max_pages': 500,
        'threads': 20,
        'request_delay': 0.1,
        'jitter': 0.1,
        'user_agent_rotation': True,
        'ip_rotation': True,
        'stealth_level': 'low'
    },
    'stealth': {
        'name': 'Stealth Scan',
        'description': 'Maximum evasion techniques with balanced testing',
        'modules': ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 
                   'headers', 'cookies', 'sensitive_data'],
        'max_depth': 3,
        'max_pages': 200,
        'threads': 3,
        'request_delay': 3.0,
        'jitter': 1.0,
        'user_agent_rotation': True,
        'ip_rotation': True,
        'stealth_level': 'maximum'
    }
}

# Path to user-defined profiles
PROFILES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             '../data/profiles.json')

# Ensure data directory exists
os.makedirs(os.path.dirname(PROFILES_PATH), exist_ok=True)

# Initialize user profiles if not exist
if not os.path.exists(PROFILES_PATH):
    with open(PROFILES_PATH, 'w') as f:
        json.dump(DEFAULT_PROFILES, f, indent=2)


@config_bp.route('/profiles', methods=['GET'])
def get_profiles():
    """
    Get all available scan profiles
    """
    try:
        with open(PROFILES_PATH, 'r') as f:
            profiles = json.load(f)
        
        return jsonify({
            'status': 'success',
            'profiles': profiles
        })
        
    except Exception as e:
        logger.error(f"Error getting profiles: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/profiles/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    """
    Get a specific scan profile
    """
    try:
        with open(PROFILES_PATH, 'r') as f:
            profiles = json.load(f)
        
        if profile_id not in profiles:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify({
            'status': 'success',
            'profile': profiles[profile_id]
        })
        
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/profiles', methods=['POST'])
def create_profile():
    """
    Create a new scan profile
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'id' not in data or 'name' not in data:
            return jsonify({'error': 'Profile ID and name are required'}), 400
        
        profile_id = data['id']
        
        # Load existing profiles
        with open(PROFILES_PATH, 'r') as f:
            profiles = json.load(f)
        
        # Check if profile ID already exists
        if profile_id in profiles:
            return jsonify({'error': 'Profile ID already exists'}), 409
        
        # Create new profile
        profiles[profile_id] = {
            'name': data['name'],
            'description': data.get('description', ''),
            'modules': data.get('modules', []),
            'max_depth': data.get('max_depth', 3),
            'max_pages': data.get('max_pages', 200),
            'threads': data.get('threads', 10),
            'request_delay': data.get('request_delay', 0.5),
            'jitter': data.get('jitter', 0.2),
            'user_agent_rotation': data.get('user_agent_rotation', True),
            'ip_rotation': data.get('ip_rotation', False),
            'stealth_level': data.get('stealth_level', 'medium')
        }
        
        # Save profiles
        with open(PROFILES_PATH, 'w') as f:
            json.dump(profiles, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': 'Profile created successfully',
            'profile': profiles[profile_id]
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/profiles/<profile_id>', methods=['PUT'])
def update_profile(profile_id):
    """
    Update an existing scan profile
    """
    try:
        data = request.get_json()
        
        # Load existing profiles
        with open(PROFILES_PATH, 'r') as f:
            profiles = json.load(f)
        
        # Check if profile exists
        if profile_id not in profiles:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Update profile fields
        if 'name' in data:
            profiles[profile_id]['name'] = data['name']
        if 'description' in data:
            profiles[profile_id]['description'] = data['description']
        if 'modules' in data:
            profiles[profile_id]['modules'] = data['modules']
        if 'max_depth' in data:
            profiles[profile_id]['max_depth'] = data['max_depth']
        if 'max_pages' in data:
            profiles[profile_id]['max_pages'] = data['max_pages']
        if 'threads' in data:
            profiles[profile_id]['threads'] = data['threads']
        if 'request_delay' in data:
            profiles[profile_id]['request_delay'] = data['request_delay']
        if 'jitter' in data:
            profiles[profile_id]['jitter'] = data['jitter']
        if 'user_agent_rotation' in data:
            profiles[profile_id]['user_agent_rotation'] = data['user_agent_rotation']
        if 'ip_rotation' in data:
            profiles[profile_id]['ip_rotation'] = data['ip_rotation']
        if 'stealth_level' in data:
            profiles[profile_id]['stealth_level'] = data['stealth_level']
        
        # Save profiles
        with open(PROFILES_PATH, 'w') as f:
            json.dump(profiles, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'profile': profiles[profile_id]
        })
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/profiles/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """
    Delete a scan profile
    """
    try:
        # Load existing profiles
        with open(PROFILES_PATH, 'r') as f:
            profiles = json.load(f)
        
        # Check if profile exists
        if profile_id not in profiles:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Don't allow deletion of default profiles
        if profile_id in DEFAULT_PROFILES:
            return jsonify({'error': 'Cannot delete default profile'}), 403
        
        # Delete profile
        del profiles[profile_id]
        
        # Save profiles
        with open(PROFILES_PATH, 'w') as f:
            json.dump(profiles, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': f'Profile {profile_id} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting profile: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/modules', methods=['GET'])
def get_modules():
    """
    Get all available security testing modules
    """
    modules = {
        'discovery': {
            'name': 'Discovery & Enumeration',
            'description': 'Identifies application structure, endpoints, and technologies',
            'passive': True
        },
        'authentication': {
            'name': 'Authentication Testing',
            'description': 'Tests for authentication vulnerabilities like weak passwords, session management issues',
            'passive': False
        },
        'injection': {
            'name': 'Injection Vulnerabilities',
            'description': 'Tests for SQL, NoSQL, and other injection attacks',
            'passive': False
        },
        'xss': {
            'name': 'Cross-Site Scripting (XSS)',
            'description': 'Tests for reflected, stored, and DOM-based XSS vulnerabilities',
            'passive': False
        },
        'csrf': {
            'name': 'Cross-Site Request Forgery',
            'description': 'Tests for CSRF vulnerabilities in forms and state-changing operations',
            'passive': False
        },
        'ssl_tls': {
            'name': 'SSL/TLS Analysis',
            'description': 'Analyzes SSL/TLS configuration and identifies weaknesses',
            'passive': True
        },
        'headers': {
            'name': 'HTTP Headers Analysis',
            'description': 'Tests for missing or misconfigured security headers',
            'passive': True
        },
        'cookies': {
            'name': 'Cookie Analysis',
            'description': 'Tests for insecure cookie configurations',
            'passive': True
        },
        'sensitive_data': {
            'name': 'Sensitive Data Exposure',
            'description': 'Identifies potentially exposed sensitive information',
            'passive': True
        },
        'brute_force': {
            'name': 'Brute Force Testing',
            'description': 'Tests resistance to brute force attacks on login and other forms',
            'passive': False
        },
        'dos_simulation': {
            'name': 'DoS Simulation',
            'description': 'Limited simulation of denial of service vulnerabilities',
            'passive': False
        },
        'file_inclusion': {
            'name': 'File Inclusion',
            'description': 'Tests for local and remote file inclusion vulnerabilities',
            'passive': False
        },
        'command_injection': {
            'name': 'Command Injection',
            'description': 'Tests for OS command injection vulnerabilities',
            'passive': False
        },
        'deserialization': {
            'name': 'Insecure Deserialization',
            'description': 'Tests for insecure deserialization vulnerabilities',
            'passive': False
        },
        'passive_vulnerability': {
            'name': 'Passive Vulnerability Detection',
            'description': 'Detects vulnerabilities without active exploitation',
            'passive': True
        }
    }
    
    return jsonify({
        'status': 'success',
        'modules': modules
    })