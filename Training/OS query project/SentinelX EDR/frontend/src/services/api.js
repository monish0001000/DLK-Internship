import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const removeAuthToken = () => {
  delete api.defaults.headers.common['Authorization'];
};

// Response interceptor for automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          const { access_token, refresh_token: new_refresh_token } = res.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', new_refresh_token);
          setAuthToken(access_token);
          originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (err) {
          // Refresh failed, logout
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const getEndpoints = () => api.get('/endpoints/');
export const getEndpoint = (id) => api.get(`/endpoints/${id}`);

export const getAlerts = () => api.get('/alerts/');
export const getAlert = (id) => api.get(`/alerts/${id}`);

export const getCases = () => api.get('/cases/');
export const getCase = (id) => api.get(`/cases/${id}`);

export const getDetectionRules = () => api.get('/rules/');
export const getDetectionRule = (id) => api.get(`/rules/${id}`);

export const getMetrics = () => api.get('/metrics/dashboard');
export const getMttd = () => api.get('/metrics/mttd');

export const getThreatIntel = () => api.get('/threat-intel/');

export const getInvestigations = () => api.get('/investigations/');

export const simulateResponse = (data) => api.post('/responses/simulate', data);
export const getResponseLogs = () => api.get('/responses/logs');

export const runThreatHunt = (query) => api.post('/threat-hunting/query', query);
export const getHuntHistory = () => api.get('/threat-hunting/history');
export const saveHunt = (data) => api.post('/threat-hunting/saved', data);
export const getSavedHunts = () => api.get('/threat-hunting/saved');

export const getSimulationScenarios = () => api.get('/simulations/scenarios');
export const runSimulation = (data) => api.post('/simulations/run', data);

export const getAlertGraph = (alertId) => api.get(`/graphs/alert/${alertId}`);
export const getEndpointGraph = (endpointId) => api.get(`/graphs/endpoint/${endpointId}`);

// Auth and Audit APIs
export const getAuditLogs = (params) => api.get('/audit/', { params });
export const getHealth = () => api.get('/health/');

export default api;
