import api from '../services/api';

export interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_by: {
    id: number | null;
    full_name: string | null;
  };
  updated_by: {
    id: number | null;
    full_name: string | null;
  };
  created_on: string | null;
  updated_on: string | null;
}

interface CreateUserData {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  password: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface UpdateUserData {
  first_name?: string;
  last_name?: string;
  email?: string;
  username?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export const getUsers = async (): Promise<User[]> => {
  const response = await api.get('/users/');
  return response.data.map((user: any): User => ({
    id: user.id,
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    username: user.username,
    is_active: user.is_active,
    is_superuser: user.is_superuser || false,
    created_by: user.created_by || { id: null, full_name: null },
    updated_by: user.updated_by || { id: null, full_name: null },
    created_on: user.created_on || null,
    updated_on: user.updated_on || null
  }));
};

export const createUser = async (userData: CreateUserData): Promise<User> => {
  try {
    const response = await api.post('/users/', userData);
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 400) {
      throw error;
    }
    throw new Error('An unexpected error occurred');
  }
};

export const updateUser = async (userId: number, userData: UpdateUserData): Promise<User> => {
  try {
    const response = await api.put(`/users/${userId}`, userData);
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 400) {
      throw error;
    }
    throw new Error('An unexpected error occurred');
  }
};

export const updatePassword = async (userId: number, newPassword: string): Promise<{ message: string }> => {
  try {
    const response = await api.post(`/users/${userId}/update-password`, { new_password: newPassword });
    return response.data;
  } catch (error) {
    throw new Error('Failed to update password');
  }
};

export const deleteUser = async (userId: number): Promise<string> => {
  try {
    const response = await api.delete(`/users/${userId}`);
    return response.data.message;
  } catch (error) {
    throw new Error('Failed to delete user');
  }
};

export const updateUserStatus = async (userId: number, isActive: boolean): Promise<{ message: string }> => {
  const response = await api.put(`/users/${userId}/update-status`, { is_active: isActive });
  return response.data;
};