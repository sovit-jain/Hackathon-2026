import axios, { AxiosHeaders } from 'axios';

// API base URL from environment variable
// REQUIRED for both development and production
const baseURL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? window.location.origin : '');

if (!baseURL && typeof window !== 'undefined') {
  console.error('NEXT_PUBLIC_API_URL environment variable is not set. API calls will fail.');
}

const api = axios.create({
  baseURL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = window.localStorage.getItem('skillbridge_token');
    console.debug('API request token present:', !!token);
    if (token) {
      if (config.headers instanceof AxiosHeaders) {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        const existingHeaders = (config.headers ?? {}) as Record<string, unknown>;
        config.headers = new AxiosHeaders({
          ...existingHeaders,
          Authorization: `Bearer ${token}`,
        });
      }
    }
  }
  return config;
});

export default api;
