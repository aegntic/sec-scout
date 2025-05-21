import apiService from './api';

// Auth state management
const authService = {
  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('accessToken');
  },
  
  // Get current user
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch (error) {
      console.error('Error parsing user data', error);
      return null;
    }
  },
  
  // Login user and store tokens
  login: async (username, password, mfaCode = null) => {
    try {
      const response = await apiService.login(username, password, mfaCode);
      const { access_token, refresh_token, user } = response.data;
      
      // Store tokens and user data
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return { success: true, user };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed'
      };
    }
  },
  
  // Logout user and clear tokens
  logout: async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await apiService.logout(refreshToken);
      }
    } catch (error) {
      console.error('Error during logout', error);
    } finally {
      // Clear local storage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    }
  },
  
  // Register new user
  register: async (username, email, password) => {
    try {
      const response = await apiService.register(username, email, password);
      return { success: true, user: response.data.user };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Registration failed'
      };
    }
  },
  
  // Check if user has specific permission
  hasPermission: (permission) => {
    const user = authService.getCurrentUser();
    if (!user) return false;
    
    // For simplicity, we're checking if the user is an admin or manager
    // In a full implementation, we would check the specific permission
    return ['ADMIN', 'MANAGER'].includes(user.role) || 
           (user.permissions && user.permissions.includes(permission));
  },
  
  // Check if setup is complete
  checkSetupStatus: async () => {
    try {
      const response = await apiService.getSetupStatus();
      return response.data;
    } catch (error) {
      console.error('Error checking setup status', error);
      return { setup_complete: false, admin_count: 0 };
    }
  },
  
  // Update user profile
  updateProfile: async (username, userData) => {
    try {
      const response = await apiService.updateUser(username, userData);
      
      // Update stored user data if it's the current user
      const currentUser = authService.getCurrentUser();
      if (currentUser && currentUser.username === username) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      return { success: true, user: response.data.user };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Profile update failed'
      };
    }
  },
  
  // Change password
  changePassword: async (username, currentPassword, newPassword) => {
    try {
      const response = await apiService.updatePassword(
        username, currentPassword, newPassword
      );
      return { success: true, message: response.data.message };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Password change failed'
      };
    }
  }
};

export default authService;