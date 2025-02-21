// src/services/api.ts

import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.API_BASE_URL, // Ensure API_BASE_URL is set in config.ts
  headers: {
    'Content-Type': 'application/json',
  },
});

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export default api;
