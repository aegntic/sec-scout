#!/usr/bin/env python3
# SecureScout - Authentication API Controller

import os
import logging
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps

from modules.auth.auth_manager import create_auth_manager, UserRole

# Initialize Blueprint
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Create auth manager
auth_manager = None

def init_auth_manager(app):
    """Initialize auth manager with app configuration."""
    global auth_manager
    
    config = {
        'jwt_secret_key': app.config.get('JWT_SECRET_KEY'),
        'access_token_lifetime_minutes': app.config.get('ACCESS_TOKEN_LIFETIME_MINUTES', 30),
        'refresh_token_lifetime_days': app.config.get('REFRESH_TOKEN_LIFETIME_DAYS', 7),
        'create_default_admin': app.config.get('CREATE_DEFAULT_ADMIN', False),
        'default_admin_username': app.config.get('DEFAULT_ADMIN_USERNAME'),
        'default_admin_password': app.config.get('DEFAULT_ADMIN_PASSWORD'),
        'default_admin_email': app.config.get('DEFAULT_ADMIN_EMAIL')
    }
    
    auth_manager = create_auth_manager(config)
    
    logger.info("Auth manager initialized")

def auth_required(permission=None):
    """
    Decorator for routes that require authentication.
    
    Args:
        permission: Optional permission required to access the route
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get auth header
            auth_header = request.headers.get('Authorization')
            
            # Check if X-API-Key header is provided
            api_key = request.headers.get('X-API-Key')
            
            if api_key:
                # Authenticate with API key
                valid, user, permissions, error = auth_manager.verify_api_key(api_key)
                
                if not valid:
                    return jsonify({'error': error}), 401
                
                # Check permission if required
                if permission and not auth_manager.check_permission(user, permission):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Set user in request context
                g.user = user
                g.permissions = permissions
                
                return f(*args, **kwargs)
            
            if not auth_header:
                return jsonify({'error': 'Authorization header required'}), 401
            
            # Check auth header format
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': 'Invalid authorization header format'}), 401
            
            token = parts[1]
            
            # Verify token
            valid, user, permissions, error = auth_manager.verify_access_token(token)
            
            if not valid:
                return jsonify({'error': error}), 401
            
            # Check permission if required
            if permission and not auth_manager.check_permission(user, permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Set user in request context
            g.user = user
            g.permissions = permissions
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    
    # Validate request
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    mfa_code = data.get('mfa_code')
    
    # Authenticate user
    success, tokens, message = auth_manager.login(username, password, mfa_code)
    
    if not success:
        return jsonify({'error': message}), 401
    
    return jsonify(tokens), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh token endpoint."""
    data = request.get_json()
    
    # Validate request
    if not data or 'refresh_token' not in data:
        return jsonify({'error': 'Refresh token required'}), 400
    
    refresh_token = data['refresh_token']
    
    # Refresh token
    success, tokens, message = auth_manager.refresh_token(refresh_token)
    
    if not success:
        return jsonify({'error': message}), 401
    
    return jsonify(tokens), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint."""
    data = request.get_json()
    
    # Validate request
    if not data or 'refresh_token' not in data:
        return jsonify({'error': 'Refresh token required'}), 400
    
    refresh_token = data['refresh_token']
    
    # Logout user
    success, message = auth_manager.logout(refresh_token)
    
    return jsonify({'message': message}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (if self-registration is enabled)."""
    # Check if self-registration is enabled
    if not current_app.config.get('ALLOW_SELF_REGISTRATION', False):
        return jsonify({'error': 'Self-registration is not enabled'}), 403
    
    data = request.get_json()
    
    # Validate request
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({'error': 'Username, password, and email required'}), 400
    
    username = data['username']
    password = data['password']
    email = data['email']
    
    # Default role for self-registration is VIEWER
    role = UserRole.VIEWER
    
    # Create user
    success, user, message = auth_manager.user_manager.create_user(
        username=username,
        email=email,
        password=password,
        role=role
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/users', methods=['GET'])
@auth_required('user:read')
def get_users():
    """Get all users (admin only)."""
    users = auth_manager.user_manager.get_users()
    
    # Convert to dict
    user_dicts = [user.to_dict() for user in users]
    
    return jsonify(user_dicts), 200

@auth_bp.route('/users/<username>', methods=['GET'])
@auth_required('user:read')
def get_user(username):
    """Get a specific user."""
    user = auth_manager.user_manager.get_user(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/users', methods=['POST'])
@auth_required('user:create')
def create_user():
    """Create a new user (admin only)."""
    data = request.get_json()
    
    # Validate request
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({'error': 'Username, password, and email required'}), 400
    
    username = data['username']
    password = data['password']
    email = data['email']
    
    # Parse role
    role_name = data.get('role', 'VIEWER')
    try:
        role = UserRole[role_name]
    except KeyError:
        return jsonify({'error': f'Invalid role: {role_name}'}), 400
    
    # Create user
    success, user, message = auth_manager.user_manager.create_user(
        username=username,
        email=email,
        password=password,
        role=role
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/users/<username>', methods=['PUT'])
@auth_required('user:update')
def update_user(username):
    """Update a user."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get current user
    current_user = g.user
    
    # Check if user is updating themselves or has admin permission
    if current_user.username != username and not auth_manager.check_permission(current_user, 'user:update'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Parse role if provided
    role = None
    if 'role' in data:
        # Only admins can change roles
        if not auth_manager.check_permission(current_user, 'user:update'):
            return jsonify({'error': 'Insufficient permissions to change role'}), 403
        
        try:
            role = UserRole[data['role']]
        except KeyError:
            return jsonify({'error': f'Invalid role: {data["role"]}'}), 400
    
    # Update user
    success, message = auth_manager.user_manager.update_user(
        username=username,
        email=data.get('email'),
        active=data.get('active'),
        role=role
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    # Get updated user
    user = auth_manager.user_manager.get_user(username)
    
    return jsonify({
        'message': message,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/users/<username>', methods=['DELETE'])
@auth_required('user:delete')
def delete_user(username):
    """Delete a user."""
    # Get current user
    current_user = g.user
    
    # Users cannot delete themselves
    if current_user.username == username:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    # Delete user
    success, message = auth_manager.user_manager.delete_user(username)
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({'message': message}), 200

@auth_bp.route('/users/<username>/password', methods=['PUT'])
@auth_required()
def update_password(username):
    """Update a user's password."""
    data = request.get_json()
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Current password and new password required'}), 400
    
    # Get current user
    current_user = g.user
    
    # Check if user is updating their own password or has admin permission
    if current_user.username != username and not auth_manager.check_permission(current_user, 'user:update'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Update password
    user = auth_manager.user_manager.get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    success, message = auth_manager.user_manager.update_password(
        user=user,
        current_password=data['current_password'],
        new_password=data['new_password']
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({'message': message}), 200

@auth_bp.route('/users/<username>/reset-password', methods=['POST'])
@auth_required('user:update')
def reset_password(username):
    """Reset a user's password (admin only)."""
    data = request.get_json()
    
    if not data or 'new_password' not in data:
        return jsonify({'error': 'New password required'}), 400
    
    # Reset password
    success, message = auth_manager.user_manager.reset_password(
        username=username,
        new_password=data['new_password']
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({'message': message}), 200

@auth_bp.route('/users/<username>/api-keys', methods=['GET'])
@auth_required()
def get_api_keys(username):
    """Get a user's API keys."""
    # Get current user
    current_user = g.user
    
    # Check if user is getting their own API keys or has admin permission
    if current_user.username != username and not auth_manager.check_permission(current_user, 'user:read'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Get user
    user = auth_manager.user_manager.get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Return API keys (excluding hash)
    api_keys = []
    for key in user.api_keys:
        key_copy = key.copy()
        key_copy.pop('hash', None)
        api_keys.append(key_copy)
    
    return jsonify(api_keys), 200

@auth_bp.route('/users/<username>/api-keys', methods=['POST'])
@auth_required()
def create_api_key(username):
    """Create a new API key for a user."""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'API key name required'}), 400
    
    # Get current user
    current_user = g.user
    
    # Check if user is creating their own API key or has admin permission
    if current_user.username != username and not auth_manager.check_permission(current_user, 'user:update'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Get user
    user = auth_manager.user_manager.get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Create API key
    expires_in_days = data.get('expires_in_days')
    if expires_in_days is not None:
        try:
            expires_in_days = int(expires_in_days)
        except ValueError:
            return jsonify({'error': 'Invalid expires_in_days value'}), 400
    
    api_key, key_metadata = auth_manager.user_manager.create_api_key_for_user(
        user=user,
        name=data['name'],
        expires_in_days=expires_in_days
    )
    
    # Remove hash from response
    key_metadata.pop('hash', None)
    
    return jsonify({
        'message': 'API key created successfully',
        'api_key': api_key,  # Full API key, only returned once
        'metadata': key_metadata
    }), 201

@auth_bp.route('/users/<username>/api-keys/<key_id>', methods=['DELETE'])
@auth_required()
def revoke_api_key(username, key_id):
    """Revoke an API key."""
    # Get current user
    current_user = g.user
    
    # Check if user is revoking their own API key or has admin permission
    if current_user.username != username and not auth_manager.check_permission(current_user, 'user:update'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Get user
    user = auth_manager.user_manager.get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Revoke API key
    success = auth_manager.user_manager.revoke_api_key(user, key_id)
    
    if not success:
        return jsonify({'error': 'API key not found'}), 404
    
    return jsonify({'message': 'API key revoked successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
@auth_required()
def get_profile():
    """Get the current user's profile."""
    # Get current user
    current_user = g.user
    
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/roles', methods=['GET'])
@auth_required()
def get_roles():
    """Get all available user roles."""
    roles = [role.name for role in UserRole]

    return jsonify(roles), 200


@auth_bp.route('/setup-status', methods=['GET'])
def setup_status():
    """Check if the app has been set up with an admin user."""
    # Check if there are any admin users
    admin_users = [user for user in auth_manager.user_manager.get_users()
                  if user.role == UserRole.ADMIN]

    return jsonify({
        'setup_complete': len(admin_users) > 0,
        'admin_count': len(admin_users)
    }), 200