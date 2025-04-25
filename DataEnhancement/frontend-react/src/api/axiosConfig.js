import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // Uses the proxy
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add response interceptor
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    if (error.code === 'ECONNREFUSED') {
      console.error('Backend connection refused - is the server running?');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
