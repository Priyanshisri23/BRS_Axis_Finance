'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { login as apiLogin, getLoggedInUser, UserInfo } from '../services/authService';
import { setAuthToken } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserInfo | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuthStatus: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserInfo | null>(null);

  const checkAuthStatus = useCallback(async (): Promise<boolean> => {
    const savedToken = localStorage.getItem('access_token');
    if (savedToken) {
      setAuthToken(savedToken);
      try {
        const userInfo = await getLoggedInUser();
        setUser(userInfo);
        setIsAuthenticated(true);
        return true;
      } catch (error) {
        console.error('Failed to get user info:', error);
        logout();
        return false;
      }
    }
    return false;
  }, []);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  const login = async (username: string, password: string) => {
    try {
      const response = await apiLogin(username, password);
      const { access_token } = response;
      
      localStorage.setItem('access_token', access_token);
      setAuthToken(access_token);

      const userInfo = await getLoggedInUser();
      setUser(userInfo);
      setIsAuthenticated(true);
    } catch (error: any) {
      console.error('Login failed:', error);
      throw new Error(error.message || 'Login failed');
    }
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    setAuthToken(null);
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, checkAuthStatus }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};