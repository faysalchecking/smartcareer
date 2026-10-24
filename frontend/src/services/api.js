import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const apiInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Include cookies
});

// Get CSRF token from cookie
function getCsrfToken() {
  const name = 'csrftoken';
  let csrftoken = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        csrftoken = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return csrftoken;
}

// Request interceptor - add CSRF token and auth headers
apiInstance.interceptors.request.use(
  (config) => {
    // Add CSRF token for non-GET requests
    if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    
    // Add auth token if exists
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
apiInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    if (error.response?.status === 403) {
      // Forbidden - permission denied
      console.error('Permission denied:', error.response.data);
    }
    return Promise.reject(error);
  }
);

export default apiInstance;