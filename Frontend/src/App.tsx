import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { LoginForm } from './components/Auth/LoginForm';
import { Dashboard } from './components/Dashboard/Dashboard';
import { UserManagement } from './components/UserManagement/UserManagement';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" toastOptions={{ duration: 4000 }} />
        <MainApp />
      </Router>
    </AuthProvider>
  );
};

const MainApp: React.FC = () => {
  const { isAuthenticated, checkAuthStatus } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = async () => {
      await checkAuthStatus();
    };
    initAuth();
  }, [checkAuthStatus]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginForm />} />
      <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />} />
      <Route path="/management" element={isAuthenticated ? <UserManagement /> : <Navigate to="/login" replace />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default App;