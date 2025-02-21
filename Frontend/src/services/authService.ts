import api from './api';

export interface UserInfo {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
  confirm_new_password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const login = async (username: string, password: string): Promise<LoginResponse> => {
  try {
    const response = await api.post<LoginResponse>('/auth/login', { username, password });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 403) {
      throw new Error('Your account is inactive. Please contact the administrator.');
    } else if (error.response && error.response.data.detail) {
      throw new Error(error.response.data.detail);
    } else {
      throw new Error('An unexpected error occurred. Please try again.');
    }
  }
};

export const getLoggedInUser = async (): Promise<UserInfo> => {
  const response = await api.get<UserInfo>('/auth/me');
  return response.data;
};

export const resetPassword = async (userId: number, newPassword: string) => {
  const response = await api.put(`/users/${userId}/update-password`, { new_password: newPassword });
  return response.data;
};

export const changePassword = async (payload: ChangePasswordPayload) => {
  const response = await api.put('/users/change-password', payload);
  return response.data;
};