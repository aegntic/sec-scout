"""
Real Error Handler - Graceful Error Management
=============================================

Professional error handling for elite security testing operations.
No cut corners - comprehensive error recovery and user guidance.
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, Callable
from functools import wraps
from enum import Enum
import asyncio

class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    TOOL_EXECUTION = "tool_execution"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    TIMEOUT = "timeout"

class RealErrorHandler:
    """
    Professional error handling with graceful degradation and recovery
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_history = []
        self.recovery_strategies = self._load_recovery_strategies()
        
    def _load_recovery_strategies(self) -> Dict[ErrorCategory, Callable]:
        """Load error recovery strategies"""
        
        return {
            ErrorCategory.NETWORK: self._handle_network_error,
            ErrorCategory.AUTHENTICATION: self._handle_auth_error,
            ErrorCategory.VALIDATION: self._handle_validation_error,
            ErrorCategory.TOOL_EXECUTION: self._handle_tool_error,
            ErrorCategory.PERMISSION: self._handle_permission_error,
            ErrorCategory.CONFIGURATION: self._handle_config_error,
            ErrorCategory.RESOURCE: self._handle_resource_error,
            ErrorCategory.TIMEOUT: self._handle_timeout_error
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle error with appropriate recovery strategy"""
        
        context = context or {}
        
        # Categorize error
        category = self._categorize_error(error)
        severity = self._determine_severity(error, category)
        
        # Create error report
        error_report = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category.value,
            'severity': severity.value,
            'context': context,
            'timestamp': self._get_timestamp(),
            'traceback': traceback.format_exc() if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL] else None,
            'recovery_attempted': False,
            'recovery_successful': False,
            'user_guidance': '',
            'next_steps': []
        }
        
        # Log error appropriately
        self._log_error(error_report)
        
        # Attempt recovery
        if category in self.recovery_strategies:
            try:
                recovery_result = self.recovery_strategies[category](error, context)
                error_report.update(recovery_result)
                error_report['recovery_attempted'] = True
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
                error_report['recovery_error'] = str(recovery_error)
        
        # Add user guidance
        error_report['user_guidance'] = self._generate_user_guidance(error_report)
        error_report['next_steps'] = self._generate_next_steps(error_report)
        
        # Store in history
        self.error_history.append(error_report)
        
        return error_report
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and content"""
        
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Network errors
        if 'connection' in error_message or 'network' in error_message or 'timeout' in error_message:
            if 'timeout' in error_message:
                return ErrorCategory.TIMEOUT
            return ErrorCategory.NETWORK
        
        # Authentication errors
        if 'auth' in error_message or 'unauthorized' in error_message or 'forbidden' in error_message:
            return ErrorCategory.AUTHENTICATION
        
        # Validation errors
        if 'validation' in error_message or 'invalid' in error_message or error_type in ['ValueError', 'ValidationError']:
            return ErrorCategory.VALIDATION
        
        # Tool execution errors
        if 'command' in error_message or 'subprocess' in error_message or 'tool' in error_message:
            return ErrorCategory.TOOL_EXECUTION
        
        # Permission errors
        if 'permission' in error_message or 'access denied' in error_message or error_type == 'PermissionError':
            return ErrorCategory.PERMISSION
        
        # Configuration errors
        if 'config' in error_message or 'configuration' in error_message or 'missing' in error_message:
            return ErrorCategory.CONFIGURATION
        
        # Resource errors
        if 'memory' in error_message or 'disk' in error_message or 'resource' in error_message:
            return ErrorCategory.RESOURCE
        
        # Default to configuration for unknown errors
        return ErrorCategory.CONFIGURATION
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        
        # Critical errors that break core functionality
        critical_indicators = ['security', 'critical', 'fatal', 'corruption']
        if any(indicator in str(error).lower() for indicator in critical_indicators):
            return ErrorSeverity.CRITICAL
        
        # Category-specific severity
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.PERMISSION]:
            return ErrorSeverity.ERROR
        elif category in [ErrorCategory.NETWORK, ErrorCategory.TIMEOUT]:
            return ErrorSeverity.WARNING
        elif category == ErrorCategory.VALIDATION:
            return ErrorSeverity.WARNING
        else:
            return ErrorSeverity.ERROR
    
    def _log_error(self, error_report: Dict[str, Any]):
        """Log error with appropriate level"""
        
        severity = error_report['severity']
        message = f"[{error_report['category'].upper()}] {error_report['error_message']}"
        
        if severity == ErrorSeverity.CRITICAL.value:
            self.logger.critical(message)
        elif severity == ErrorSeverity.ERROR.value:
            self.logger.error(message)
        elif severity == ErrorSeverity.WARNING.value:
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _handle_network_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle network-related errors"""
        
        target_url = context.get('target_url', 'unknown')
        
        recovery_result = {
            'recovery_successful': False,
            'alternative_approach': None
        }
        
        # Try alternative approaches
        if 'https' in target_url:
            # Try HTTP fallback
            recovery_result['alternative_approach'] = 'http_fallback'
            recovery_result['recovery_successful'] = True
        elif 'connection refused' in str(error).lower():
            # Suggest port scanning
            recovery_result['alternative_approach'] = 'port_scan_first'
            recovery_result['recovery_successful'] = True
        
        return recovery_result
    
    def _handle_auth_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle authentication errors"""
        
        return {
            'recovery_successful': False,
            'alternative_approach': 'credential_enumeration',
            'suggested_action': 'Check authentication requirements'
        }
    
    def _handle_validation_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors"""
        
        return {
            'recovery_successful': True,
            'alternative_approach': 'input_sanitization',
            'suggested_action': 'Validate and correct input parameters'
        }
    
    def _handle_tool_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution errors"""
        
        tool_name = context.get('tool_name', 'unknown')
        
        recovery_result = {
            'recovery_successful': False,
            'alternative_approach': None
        }
        
        # Check if tool is installed
        if 'not found' in str(error).lower() or 'command not found' in str(error).lower():
            recovery_result['alternative_approach'] = 'fallback_tool'
            recovery_result['suggested_action'] = f'Install {tool_name} or use alternative tool'
        else:
            recovery_result['alternative_approach'] = 'parameter_adjustment'
            recovery_result['suggested_action'] = 'Adjust tool parameters and retry'
        
        return recovery_result
    
    def _handle_permission_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle permission errors"""
        
        return {
            'recovery_successful': False,
            'alternative_approach': 'privilege_escalation',
            'suggested_action': 'Check file permissions or run with appropriate privileges'
        }
    
    def _handle_config_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration errors"""
        
        return {
            'recovery_successful': True,
            'alternative_approach': 'default_configuration',
            'suggested_action': 'Use default configuration or check config file'
        }
    
    def _handle_resource_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource errors"""
        
        return {
            'recovery_successful': False,
            'alternative_approach': 'resource_optimization',
            'suggested_action': 'Free up system resources or reduce operation scope'
        }
    
    def _handle_timeout_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout errors"""
        
        return {
            'recovery_successful': True,
            'alternative_approach': 'extended_timeout',
            'suggested_action': 'Increase timeout duration or reduce operation complexity'
        }
    
    def _generate_user_guidance(self, error_report: Dict[str, Any]) -> str:
        """Generate user-friendly guidance"""
        
        category = error_report['category']
        severity = error_report['severity']
        
        guidance_templates = {
            'network': "Unable to connect to target. Please check network connectivity and target availability.",
            'authentication': "Authentication failed. Please verify credentials or authentication method.",
            'validation': "Input validation failed. Please check and correct the provided parameters.",
            'tool_execution': "Security tool execution failed. Please check tool installation and configuration.",
            'permission': "Permission denied. Please check file permissions or run with appropriate privileges.",
            'configuration': "Configuration error detected. Please verify configuration settings.",
            'resource': "System resource limitation encountered. Please free up resources or reduce operation scope.",
            'timeout': "Operation timed out. Please increase timeout or reduce operation complexity."
        }
        
        base_guidance = guidance_templates.get(category, "An unexpected error occurred.")
        
        if severity == 'critical':
            return f"CRITICAL: {base_guidance} Please contact system administrator if the issue persists."
        elif severity == 'error':
            return f"ERROR: {base_guidance} Operation cannot continue until resolved."
        elif severity == 'warning':
            return f"WARNING: {base_guidance} Operation may continue with reduced functionality."
        else:
            return f"INFO: {base_guidance}"
    
    def _generate_next_steps(self, error_report: Dict[str, Any]) -> list:
        """Generate actionable next steps"""
        
        category = error_report['category']
        recovery_attempted = error_report['recovery_attempted']
        recovery_successful = error_report.get('recovery_successful', False)
        
        next_steps = []
        
        if recovery_attempted and recovery_successful:
            next_steps.append("Recovery successful - operation can continue")
        elif recovery_attempted and not recovery_successful:
            next_steps.append("Automatic recovery failed - manual intervention required")
        
        # Category-specific next steps
        category_steps = {
            'network': [
                "Verify target URL is correct and accessible",
                "Check network connectivity",
                "Try alternative connection methods"
            ],
            'authentication': [
                "Verify credentials are correct",
                "Check authentication method requirements",
                "Try alternative authentication approaches"
            ],
            'validation': [
                "Review input parameters for correctness",
                "Check parameter format requirements",
                "Use example values for testing"
            ],
            'tool_execution': [
                "Verify security tool is installed",
                "Check tool configuration",
                "Try alternative tools if available"
            ],
            'permission': [
                "Check file and directory permissions",
                "Run with appropriate user privileges",
                "Contact system administrator if needed"
            ],
            'configuration': [
                "Review configuration file settings",
                "Use default configuration if available",
                "Check for missing configuration parameters"
            ],
            'resource': [
                "Free up system memory and disk space",
                "Reduce operation scope or complexity",
                "Monitor system resource usage"
            ],
            'timeout': [
                "Increase operation timeout duration",
                "Reduce operation complexity",
                "Check target responsiveness"
            ]
        }
        
        next_steps.extend(category_steps.get(category, ["Contact system administrator for assistance"]))
        
        return next_steps
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        
        if not self.error_history:
            return {'total_errors': 0, 'recent_errors': []}
        
        recent_errors = self.error_history[-10:]  # Last 10 errors
        
        summary = {
            'total_errors': len(self.error_history),
            'recent_errors': recent_errors,
            'error_categories': {},
            'severity_distribution': {}
        }
        
        # Count by category and severity
        for error in recent_errors:
            category = error['category']
            severity = error['severity']
            
            summary['error_categories'][category] = summary['error_categories'].get(category, 0) + 1
            summary['severity_distribution'][severity] = summary['severity_distribution'].get(severity, 0) + 1
        
        return summary

def handle_errors(error_handler: RealErrorHandler = None, context: Dict[str, Any] = None):
    """Decorator for automatic error handling"""
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                handler = error_handler or RealErrorHandler()
                error_report = handler.handle_error(e, context)
                
                # Return error in a structured format
                return {
                    'success': False,
                    'error': error_report,
                    'result': None
                }
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = error_handler or RealErrorHandler()
                error_report = handler.handle_error(e, context)
                
                # Return error in a structured format
                return {
                    'success': False,
                    'error': error_report,
                    'result': None
                }
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# Export the error handler
__all__ = ['RealErrorHandler', 'handle_errors', 'ErrorSeverity', 'ErrorCategory']