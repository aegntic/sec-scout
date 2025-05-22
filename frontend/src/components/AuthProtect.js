import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import authService from '../services/auth';

/**
 * Higher-order component that protects routes requiring authentication
 * 
 * @param {Object} props - Component props
 * @param {React.Component} props.children - Child components to render when authenticated
 * @param {string[]} props.requiredPermissions - Optional permissions required to access this route
 * @returns {React.Component} Protected route component
 */
const AuthProtect = ({ children, requiredPermissions = [] }) => {
  const location = useLocation();
  const isAuthenticated = authService.isAuthenticated();
  
  // Check if user has required permissions
  const hasRequiredPermissions = requiredPermissions.length > 0
    ? requiredPermissions.every(perm => authService.hasPermission(perm))
    : true;
  
  // Refresh the user's token silently on component mount
  useEffect(() => {
    const refreshToken = async () => {
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await authService.refreshToken(refreshToken);
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);
        }
      } catch (error) {
        console.error('Failed to refresh token', error);
        // Let the API interceptor handle the failed refresh
      }
    };

    if (isAuthenticated) {
      refreshToken();
    }
  }, [isAuthenticated]);
  
  if (!isAuthenticated) {
    // Redirect to login page but save the current location to redirect back after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  if (!hasRequiredPermissions) {
    // User is authenticated but doesn't have required permissions
    return <Navigate to="/unauthorized" replace />;
  }
  
  // User is authenticated and has required permissions
  return children;
};

export default AuthProtect;