import axios from 'axios';

// Create API client
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API services
const apiService = {
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