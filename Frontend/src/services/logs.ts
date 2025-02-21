import api from './api';

export const getLogs = async () => {
  try {
    const response = await api.get('/logs/logs'); // Correct API endpoint
    console.dir(response, { depth: null });
    return response;
  } catch (error) {
    console.error('Error fetching logs:', error);
    throw error;
  }
};
