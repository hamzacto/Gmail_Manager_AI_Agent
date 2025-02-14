import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuthStore } from '../stores/auth';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || 'An error occurred';
    toast.error(message);
    if (error.response?.status === 401) {
      useAuthStore.getState().setToken(null);
    }
    return Promise.reject(error);
  }
);

export default api;