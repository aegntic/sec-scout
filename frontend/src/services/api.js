import axios from 'axios';

// Create API client
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Send cookies with requests
});

// Add request interceptor for authorization
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for handling token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // If the error is 401 (Unauthorized) and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Try to get a new token
        const response = await axios.post(`${API_URL}/api/auth/refresh`, {
          refresh_token: refreshToken
        });

        // Store the new tokens
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);

        // Update the authorization header
        originalRequest.headers.Authorization = `Bearer ${access_token}`;

        // Retry the original request
        return axios(originalRequest);
      } catch (error) {
        // If refresh fails, clear tokens and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');

        // If we're in a browser environment
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }

        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

// API services
const apiService = {
  // Auth services
  login: (username, password, mfaCode = null) => {
    const payload = { username, password };
    if (mfaCode) {
      payload.mfa_code = mfaCode;
    }
    return api.post('/api/auth/login', payload);
  },

  logout: (refreshToken) => {
    return api.post('/api/auth/logout', { refresh_token: refreshToken });
  },

  register: (username, email, password) => {
    return api.post('/api/auth/register', { username, email, password });
  },

  refreshToken: (refreshToken) => {
    return api.post('/api/auth/refresh', { refresh_token: refreshToken });
  },

  getProfile: () => {
    return api.get('/api/auth/profile');
  },

  updatePassword: (username, currentPassword, newPassword) => {
    return api.put(`/api/auth/users/${username}/password`, {
      current_password: currentPassword,
      new_password: newPassword
    });
  },

  getUsers: () => {
    return api.get('/api/auth/users');
  },

  createUser: (userData) => {
    return api.post('/api/auth/users', userData);
  },

  updateUser: (username, userData) => {
    return api.put(`/api/auth/users/${username}`, userData);
  },

  deleteUser: (username) => {
    return api.delete(`/api/auth/users/${username}`);
  },

  createApiKey: (username, name, expiresInDays = null) => {
    const payload = { name };
    if (expiresInDays) {
      payload.expires_in_days = expiresInDays;
    }
    return api.post(`/api/auth/users/${username}/api-keys`, payload);
  },

  getApiKeys: (username) => {
    return api.get(`/api/auth/users/${username}/api-keys`);
  },

  revokeApiKey: (username, keyId) => {
    return api.delete(`/api/auth/users/${username}/api-keys/${keyId}`);
  },

  getRoles: () => {
    return api.get('/api/auth/roles');
  },

  getSetupStatus: () => {
    return api.get('/api/auth/setup-status');
  },

  // Health check
  healthCheck: () => {
    return api.get('/api/health');
  },

  // Scan services
  startScan: (scanConfig) => {
    return api.post('/api/scan/start', scanConfig);
  },

  getScanStatus: (scanId) => {
    return api.get(`/api/scan/status/${scanId}`);
  },

  listScans: () => {
    return api.get('/api/scan/list');
  },

  stopScan: (scanId) => {
    return api.post(`/api/scan/stop/${scanId}`);
  },

  deleteScan: (scanId) => {
    return api.delete(`/api/scan/delete/${scanId}`);
  },

  // Reports services
  generateReport: (scanId) => {
    return api.post(`/api/report/generate/${scanId}`);
  },

  listReports: () => {
    return api.get('/api/report/list');
  },

  downloadReport: (filename) => {
    return api.get(`/api/report/download/${filename}`);
  },

  deleteReport: (filename) => {
    return api.delete(`/api/report/delete/${filename}`);
  },

  // Config services
  getProfiles: () => {
    return api.get('/api/config/profiles');
  },

  getProfile: (profileId) => {
    return api.get(`/api/config/profiles/${profileId}`);
  },

  createProfile: (profile) => {
    return api.post('/api/config/profiles', profile);
  },

  updateProfile: (profileId, profile) => {
    return api.put(`/api/config/profiles/${profileId}`, profile);
  },

  deleteProfile: (profileId) => {
    return api.delete(`/api/config/profiles/${profileId}`);
  },

  getModules: () => {
    return api.get('/api/config/modules');
  }
};

export default apiService;