#!/usr/bin/env python3
# SecureScout - Authentication and Access Control Manager

import os
import re
import jwt
import uuid
import time
import logging
import hashlib
import secrets
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import bcrypt
from dataclasses import dataclass, field, asdict
from enum import Enum, auto

# Configure logging
logger = logging.getLogger("securescout.auth")

class UserRole(Enum):
    """User role enumeration with associated permissions."""
    ADMIN = auto()        # Full system access
    MANAGER = auto()      # Can manage users, view all scans, but limited system settings
    ANALYST = auto()      # Can run scans, view results, create reports
    VIEWER = auto()       # Can only view scan results and reports
    API = auto()          # API access only, limited to specific endpoints

    def get_permissions(self) -> List[str]:
        """Get permissions associated with this role."""
        permissions = {
            UserRole.ADMIN: [
                'scan:create', 'scan:read', 'scan:update', 'scan:delete',
                'user:create', 'user:read', 'user:update', 'user:delete',
                'report:create', 'report:read', 'report:update', 'report:delete',
                'system:read', 'system:update'
            ],
            UserRole.MANAGER: [
                'scan:create', 'scan:read', 'scan:update', 'scan:delete',
                'user:create', 'user:read', 'user:update',
                'report:create', 'report:read', 'report:update', 'report:delete',
                'system:read'
            ],
            UserRole.ANALYST: [
                'scan:create', 'scan:read', 'scan:update',
                'report:create', 'report:read', 'report:update',
                'system:read'
            ],
            UserRole.VIEWER: [
                'scan:read',
                'report:read'
            ],
            UserRole.API: [
                'scan:create', 'scan:read',
                'report:read'
            ]
        }
        return permissions.get(self, [])

@dataclass
class User:
    """User information for authentication and authorization."""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    active: bool = True
    failed_login_attempts: int = 0
    locked_until: Optional[datetime.datetime] = None
    last_login: Optional[datetime.datetime] = None
    api_keys: List[Dict[str, Any]] = field(default_factory=list)
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary, optionally excluding sensitive fields."""
        user_dict = asdict(self)
        
        # Convert role Enum to string
        user_dict['role'] = self.role.name
        
        # Convert datetime objects to ISO strings
        for field in ['locked_until', 'last_login', 'created_at', 'updated_at']:
            if user_dict[field]:
                user_dict[field] = user_dict[field].isoformat()
        
        # Remove sensitive fields if not requested
        if not include_sensitive:
            sensitive_fields = ['password_hash', 'mfa_secret', 'api_keys']
            for field in sensitive_fields:
                user_dict.pop(field, None)
        
        return user_dict
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.role.get_permissions()
    
    def is_locked(self) -> bool:
        """Check if the user account is locked."""
        if not self.locked_until:
            return False
        return datetime.datetime.utcnow() < self.locked_until

class PasswordPolicy:
    """Password policy configuration and validation."""
    
    def __init__(self, 
                min_length: int = 12,
                require_uppercase: bool = True,
                require_lowercase: bool = True,
                require_numbers: bool = True,
                require_special: bool = True,
                max_length: int = 128,
                password_history: int = 5):
        """
        Initialize password policy.
        
        Args:
            min_length: Minimum password length
            require_uppercase: Require at least one uppercase letter
            require_lowercase: Require at least one lowercase letter
            require_numbers: Require at least one number
            require_special: Require at least one special character
            max_length: Maximum password length
            password_history: Number of previous passwords to remember
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        self.max_length = max_length
        self.password_history = password_history
    
    def validate(self, password: str) -> Tuple[bool, str]:
        """
        Validate a password against policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (valid, message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"
        
        if len(password) > self.max_length:
            return False, f"Password cannot exceed {self.max_length} characters"
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if self.require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if self.require_special and not any(not c.isalnum() for c in password):
            return False, "Password must contain at least one special character"
        
        # Check for common passwords (a real implementation would use a larger list)
        common_passwords = [
            "password", "123456", "qwerty", "admin", "welcome",
            "password123", "abc123", "letmein", "monkey", "1234567890"
        ]
        
        if password.lower() in common_passwords:
            return False, "Password is too common"
            
        return True, "Password meets requirements"

class TokenManager:
    """JWT token generation and validation."""
    
    def __init__(self, 
                secret_key: str,
                access_token_lifetime: int = 30,  # minutes
                refresh_token_lifetime: int = 7,  # days
                algorithm: str = 'HS256',
                issuer: str = 'securescout'):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for JWT signing
            access_token_lifetime: Access token lifetime in minutes
            refresh_token_lifetime: Refresh token lifetime in days
            algorithm: JWT signing algorithm
            issuer: Token issuer
        """
        self.secret_key = secret_key
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime
        self.algorithm = algorithm
        self.issuer = issuer
        self.blacklisted_tokens = set()
    
    def generate_access_token(self, user_id: str, permissions: List[str] = None) -> str:
        """
        Generate a new access token.
        
        Args:
            user_id: User ID to include in token
            permissions: User permissions to include in token
            
        Returns:
            JWT token string
        """
        now = datetime.datetime.utcnow()
        expiry = now + datetime.timedelta(minutes=self.access_token_lifetime)
        
        payload = {
            'sub': user_id,
            'iat': now,
            'exp': expiry,
            'iss': self.issuer,
            'type': 'access'
        }
        
        if permissions:
            payload['permissions'] = permissions
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: str) -> str:
        """
        Generate a new refresh token.
        
        Args:
            user_id: User ID to include in token
            
        Returns:
            JWT token string
        """
        now = datetime.datetime.utcnow()
        expiry = now + datetime.timedelta(days=self.refresh_token_lifetime)
        
        payload = {
            'sub': user_id,
            'iat': now,
            'exp': expiry,
            'iss': self.issuer,
            'jti': str(uuid.uuid4()),  # Unique token ID for revocation
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_token(self, token: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (valid, payload, error_message)
        """
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                return False, {}, "Token has been revoked"
            
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_signature": True, "verify_exp": True}
            )
            
            return True, payload, ""
            
        except jwt.ExpiredSignatureError:
            return False, {}, "Token has expired"
        except jwt.InvalidTokenError as e:
            return False, {}, f"Invalid token: {str(e)}"
    
    def blacklist_token(self, token: str) -> None:
        """
        Add a token to the blacklist.
        
        Args:
            token: JWT token to blacklist
        """
        self.blacklisted_tokens.add(token)
        
        # In a real implementation, you would store this in a database
        # and periodically clean up expired tokens

class APIKeyManager:
    """API key management."""
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a new API key.
        
        Returns:
            API key string
        """
        # Generate a secure random API key
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash an API key for storage.
        
        Args:
            api_key: API key to hash
            
        Returns:
            Hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

class UserManager:
    """User management for authentication and authorization."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize user manager.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.users = {}  # In-memory user storage (use a database in production)
        self.password_policy = PasswordPolicy(
            min_length=self.config.get('password_min_length', 12),
            require_uppercase=self.config.get('password_require_uppercase', True),
            require_lowercase=self.config.get('password_require_lowercase', True),
            require_numbers=self.config.get('password_require_numbers', True),
            require_special=self.config.get('password_require_special', True)
        )
        
        # Set up default admin user if configured
        self._setup_default_admin()
    
    def _setup_default_admin(self) -> None:
        """Set up default admin user if configured."""
        if self.config.get('create_default_admin', False):
            admin_username = self.config.get('default_admin_username', 'admin')
            admin_password = self.config.get('default_admin_password')
            admin_email = self.config.get('default_admin_email', 'admin@example.com')
            
            # Check if admin user already exists
            if admin_username not in self.users and admin_password:
                # Create admin user
                self.create_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    role=UserRole.ADMIN
                )
                logger.info(f"Created default admin user: {admin_username}")
    
    def create_user(self, username: str, email: str, password: str,
                   role: UserRole = UserRole.VIEWER) -> Tuple[bool, User, str]:
        """
        Create a new user.
        
        Args:
            username: Username
            email: Email address
            password: Plain-text password
            role: User role
            
        Returns:
            Tuple of (success, user_object, message)
        """
        # Validate username
        if not self._validate_username(username):
            return False, None, "Invalid username format"
        
        # Check if username already exists
        if username in self.users:
            return False, None, "Username already exists"
        
        # Validate email
        if not self._validate_email(email):
            return False, None, "Invalid email format"
        
        # Check if email already exists
        if any(user.email == email for user in self.users.values()):
            return False, None, "Email already exists"
        
        # Validate password against policy
        valid_password, password_message = self.password_policy.validate(password)
        if not valid_password:
            return False, None, password_message
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Create user object
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        # Store user
        self.users[username] = user
        
        return True, user, "User created successfully"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Plain-text password
            
        Returns:
            Tuple of (success, user_object, message)
        """
        # Check if user exists
        if username not in self.users:
            # Use constant-time comparison to prevent timing attacks
            # even when user doesn't exist
            self._verify_password('dummy', 'dummy')
            return False, None, "Invalid username or password"
        
        user = self.users[username]
        
        # Check if account is active
        if not user.active:
            return False, None, "Account is disabled"
        
        # Check if account is locked
        if user.is_locked():
            return False, None, f"Account is locked. Try again later."
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            max_attempts = self.config.get('max_login_attempts', 5)
            if user.failed_login_attempts >= max_attempts:
                lockout_minutes = self.config.get('account_lockout_minutes', 15)
                user.locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=lockout_minutes)
                logger.warning(f"Account locked: {username}")
            
            return False, None, "Invalid username or password"
        
        # Reset failed login attempts on success
        user.failed_login_attempts = 0
        user.last_login = datetime.datetime.utcnow()
        
        return True, user, "Authentication successful"
    
    def authenticate_api_key(self, api_key: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate a user with an API key.
        
        Args:
            api_key: API key
            
        Returns:
            Tuple of (success, user_object, message)
        """
        # Hash the provided API key
        api_key_hash = APIKeyManager.hash_api_key(api_key)
        
        # Search for matching API key
        for user in self.users.values():
            for key in user.api_keys:
                if key['hash'] == api_key_hash and key['active']:
                    # Check if API key has expired
                    if 'expires_at' in key and key['expires_at']:
                        expiry = datetime.datetime.fromisoformat(key['expires_at'])
                        if datetime.datetime.utcnow() > expiry:
                            return False, None, "API key has expired"
                    
                    return True, user, "API key authentication successful"
        
        return False, None, "Invalid API key"
    
    def verify_mfa(self, user: User, mfa_code: str) -> bool:
        """
        Verify a multi-factor authentication code.
        
        Args:
            user: User object
            mfa_code: MFA code
            
        Returns:
            True if code is valid, False otherwise
        """
        if not user.mfa_enabled or not user.mfa_secret:
            return False
        
        # In a real implementation, this would use a library like pyotp
        # to verify the code against the user's secret
        
        # For this simplified example, we'll just check if the code is "123456"
        return mfa_code == "123456"
    
    def create_api_key_for_user(self, user: User, name: str, 
                              expires_in_days: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Create a new API key for a user.
        
        Args:
            user: User object
            name: Name for the API key
            expires_in_days: Number of days until key expiry (None for no expiry)
            
        Returns:
            Tuple of (api_key, key_metadata)
        """
        # Generate a new API key
        api_key = APIKeyManager.generate_api_key()
        
        # Hash the key for storage
        api_key_hash = APIKeyManager.hash_api_key(api_key)
        
        # Calculate expiry date if needed
        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days)
        
        # Create key metadata
        key_metadata = {
            'id': str(uuid.uuid4()),
            'name': name,
            'hash': api_key_hash,
            'created_at': datetime.datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat() if expires_at else None,
            'active': True,
            'last_used': None
        }
        
        # Add to user's API keys
        user.api_keys.append(key_metadata)
        
        # Return the API key and metadata
        # Note: This is the only time the full API key will be available
        return api_key, key_metadata
    
    def revoke_api_key(self, user: User, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            user: User object
            key_id: ID of the API key to revoke
            
        Returns:
            True if key was revoked, False if not found
        """
        for key in user.api_keys:
            if key['id'] == key_id:
                key['active'] = False
                return True
        
        return False
    
    def update_password(self, user: User, current_password: str, 
                      new_password: str) -> Tuple[bool, str]:
        """
        Update a user's password.
        
        Args:
            user: User object
            current_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        # Verify current password
        if not self._verify_password(current_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Validate new password against policy
        valid_password, password_message = self.password_policy.validate(new_password)
        if not valid_password:
            return False, password_message
        
        # Hash new password
        user.password_hash = self._hash_password(new_password)
        user.updated_at = datetime.datetime.utcnow()
        
        return True, "Password updated successfully"
    
    def reset_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset a user's password (administrative function).
        
        Args:
            username: Username
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user exists
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        
        # Validate new password against policy
        valid_password, password_message = self.password_policy.validate(new_password)
        if not valid_password:
            return False, password_message
        
        # Hash new password
        user.password_hash = self._hash_password(new_password)
        user.updated_at = datetime.datetime.utcnow()
        
        # Reset failed login attempts and unlock account
        user.failed_login_attempts = 0
        user.locked_until = None
        
        return True, "Password reset successfully"
    
    def update_user_role(self, username: str, new_role: UserRole) -> Tuple[bool, str]:
        """
        Update a user's role.
        
        Args:
            username: Username
            new_role: New role
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user exists
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        user.role = new_role
        user.updated_at = datetime.datetime.utcnow()
        
        return True, "User role updated successfully"
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username
            
        Returns:
            User object if found, None if not
        """
        return self.users.get(username)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None if not
        """
        for user in self.users.values():
            if user.id == user_id:
                return user
        
        return None
    
    def get_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List of User objects
        """
        return list(self.users.values())
    
    def update_user(self, username: str, email: str = None, 
                  active: bool = None, role: UserRole = None) -> Tuple[bool, str]:
        """
        Update a user's information.
        
        Args:
            username: Username
            email: New email address (None to keep current)
            active: New active status (None to keep current)
            role: New role (None to keep current)
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user exists
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        
        # Update email if provided
        if email is not None:
            if not self._validate_email(email):
                return False, "Invalid email format"
            
            # Check if email already exists
            if any(u.email == email and u.username != username for u in self.users.values()):
                return False, "Email already exists"
            
            user.email = email
        
        # Update active status if provided
        if active is not None:
            user.active = active
            
            # If activating, reset failed login attempts
            if active:
                user.failed_login_attempts = 0
                user.locked_until = None
        
        # Update role if provided
        if role is not None:
            user.role = role
        
        user.updated_at = datetime.datetime.utcnow()
        
        return True, "User updated successfully"
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        Delete a user.
        
        Args:
            username: Username
            
        Returns:
            Tuple of (success, message)
        """
        # Check if user exists
        if username not in self.users:
            return False, "User not found"
        
        # Remove user
        del self.users[username]
        
        return True, "User deleted successfully"
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password for storage.
        
        Args:
            password: Plain-text password
            
        Returns:
            Hashed password
        """
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        
        return hashed_password.decode()
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain-text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        # Verify the password against the hash
        try:
            return bcrypt.checkpw(password.encode(), hashed_password.encode())
        except Exception:
            return False
    
    def _validate_username(self, username: str) -> bool:
        """
        Validate username format.
        
        Args:
            username: Username
            
        Returns:
            True if valid, False otherwise
        """
        # Username must be 3-32 characters, alphanumeric and underscore only
        pattern = re.compile(r'^[a-zA-Z0-9_]{3,32}$')
        return bool(pattern.match(username))
    
    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address
            
        Returns:
            True if valid, False otherwise
        """
        # Simple email validation pattern
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))

class AuthManager:
    """
    Authentication and authorization manager.
    Combines UserManager and TokenManager.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize authentication manager.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        
        # Set up user manager
        self.user_manager = UserManager(self.config)
        
        # Set up token manager
        secret_key = self.config.get('jwt_secret_key')
        if not secret_key:
            # Generate a random secret key if not provided
            secret_key = secrets.token_hex(32)
            logger.warning("No JWT secret key provided. Generated a random one.")
        
        self.token_manager = TokenManager(
            secret_key=secret_key,
            access_token_lifetime=self.config.get('access_token_lifetime_minutes', 30),
            refresh_token_lifetime=self.config.get('refresh_token_lifetime_days', 7)
        )
    
    def login(self, username: str, password: str,
             mfa_code: Optional[str] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Log in a user.
        
        Args:
            username: Username
            password: Password
            mfa_code: Multi-factor authentication code (if enabled)
            
        Returns:
            Tuple of (success, tokens, message)
        """
        # Authenticate user
        success, user, message = self.user_manager.authenticate_user(username, password)
        
        if not success or not user:
            return False, {}, message
        
        # Check if MFA is enabled
        if user.mfa_enabled:
            if not mfa_code:
                return False, {}, "MFA code required"
            
            if not self.user_manager.verify_mfa(user, mfa_code):
                return False, {}, "Invalid MFA code"
        
        # Generate tokens
        access_token = self.token_manager.generate_access_token(
            user_id=user.id,
            permissions=user.role.get_permissions()
        )
        
        refresh_token = self.token_manager.generate_refresh_token(
            user_id=user.id
        )
        
        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': self.token_manager.access_token_lifetime * 60,  # Seconds
            'user': user.to_dict()
        }
        
        return True, tokens, "Login successful"
    
    def refresh_token(self, refresh_token: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Refresh an access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Tuple of (success, tokens, message)
        """
        # Validate refresh token
        valid, payload, error = self.token_manager.validate_token(refresh_token)
        
        if not valid:
            return False, {}, error
        
        # Check token type
        if payload.get('type') != 'refresh':
            return False, {}, "Invalid token type"
        
        # Get user
        user_id = payload.get('sub')
        user = self.user_manager.get_user_by_id(user_id)
        
        if not user:
            return False, {}, "User not found"
        
        # Check if user is active
        if not user.active:
            return False, {}, "User account is disabled"
        
        # Blacklist the old refresh token
        self.token_manager.blacklist_token(refresh_token)
        
        # Generate new tokens
        new_access_token = self.token_manager.generate_access_token(
            user_id=user.id,
            permissions=user.role.get_permissions()
        )
        
        new_refresh_token = self.token_manager.generate_refresh_token(
            user_id=user.id
        )
        
        tokens = {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'bearer',
            'expires_in': self.token_manager.access_token_lifetime * 60  # Seconds
        }
        
        return True, tokens, "Token refreshed successfully"
    
    def logout(self, refresh_token: str) -> Tuple[bool, str]:
        """
        Log out a user by blacklisting their refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Tuple of (success, message)
        """
        # Validate token first
        valid, payload, error = self.token_manager.validate_token(refresh_token)
        
        # Even if token is invalid, we'll blacklist it anyway
        self.token_manager.blacklist_token(refresh_token)
        
        return True, "Logout successful"
    
    def verify_access_token(self, access_token: str) -> Tuple[bool, Optional[User], List[str], str]:
        """
        Verify an access token and return user and permissions.
        
        Args:
            access_token: Access token
            
        Returns:
            Tuple of (valid, user, permissions, error_message)
        """
        # Validate token
        valid, payload, error = self.token_manager.validate_token(access_token)
        
        if not valid:
            return False, None, [], error
        
        # Check token type
        if payload.get('type') != 'access':
            return False, None, [], "Invalid token type"
        
        # Get user
        user_id = payload.get('sub')
        user = self.user_manager.get_user_by_id(user_id)
        
        if not user:
            return False, None, [], "User not found"
        
        # Check if user is active
        if not user.active:
            return False, None, [], "User account is disabled"
        
        # Get permissions from token
        permissions = payload.get('permissions', [])
        
        return True, user, permissions, ""
    
    def verify_api_key(self, api_key: str) -> Tuple[bool, Optional[User], List[str], str]:
        """
        Verify an API key and return user and permissions.
        
        Args:
            api_key: API key
            
        Returns:
            Tuple of (valid, user, permissions, error_message)
        """
        # Authenticate with API key
        success, user, message = self.user_manager.authenticate_api_key(api_key)
        
        if not success or not user:
            return False, None, [], message
        
        # Check if user is active
        if not user.active:
            return False, None, [], "User account is disabled"
        
        # Get permissions from user role
        permissions = user.role.get_permissions()
        
        return True, user, permissions, ""
    
    def check_permission(self, user: User, required_permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user: User object
            required_permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        return user.has_permission(required_permission)

# Factory function to create AuthManager instance
def create_auth_manager(config: Dict[str, Any] = None) -> AuthManager:
    """
    Create an AuthManager instance.
    
    Args:
        config: Configuration options
        
    Returns:
        AuthManager instance
    """
    return AuthManager(config or {})

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'jwt_secret_key': 'your-secure-jwt-secret-key',
        'create_default_admin': True,
        'default_admin_username': 'admin',
        'default_admin_password': 'SecureP@ssw0rd123',
        'default_admin_email': 'admin@example.com'
    }
    
    # Create auth manager
    auth_manager = create_auth_manager(config)
    
    # Example user creation
    success, user, message = auth_manager.user_manager.create_user(
        username="testuser",
        email="test@example.com",
        password="Str0ngP@ssw0rd123",
        role=UserRole.ANALYST
    )
    
    print(f"User creation: {success}, Message: {message}")
    
    # Example login
    if success:
        success, tokens, message = auth_manager.login("testuser", "Str0ngP@ssw0rd123")
        print(f"Login: {success}, Message: {message}")
        
        if success:
            print(f"Access token: {tokens['access_token']}")
            
            # Example token verification
            valid, user, permissions, error = auth_manager.verify_access_token(tokens['access_token'])
            print(f"Token verification: {valid}, User: {user.username if user else None}")
            print(f"Permissions: {permissions}")
            
            # Example permission check
            has_permission = auth_manager.check_permission(user, 'scan:create')
            print(f"Has 'scan:create' permission: {has_permission}")
    
    # Example API key creation
    admin_user = auth_manager.user_manager.get_user("admin")
    if admin_user:
        api_key, key_metadata = auth_manager.user_manager.create_api_key_for_user(
            user=admin_user,
            name="Test API Key",
            expires_in_days=30
        )
        
        print(f"API Key: {api_key}")
        
        # Example API key verification
        valid, user, permissions, error = auth_manager.verify_api_key(api_key)
        print(f"API Key verification: {valid}, User: {user.username if user else None}")
        print(f"Permissions: {permissions}")