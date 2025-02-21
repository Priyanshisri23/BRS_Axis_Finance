import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import ProcessTrigger from '../ProcessTrigger';
import ProcessLogs from '../ProcessLogs';
import Header from '../Header/Header';
import { UserManagement } from '../UserManagement/UserManagement';
import { getLoggedInUser } from '../../services/authService';
import { toast } from 'react-hot-toast';

// Define UserInfo type based on the getLoggedInUser return type
interface UserInfo {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
}

const IDLE_TIMEOUT = 1000 * 60 * 5; // 5 minutes

export const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [showUserManagement, setShowUserManagement] = useState(false);

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const response = await getLoggedInUser();
        setUserInfo(response);
        toast.success('Welcome back!');
      } catch (error) {
        console.error('Error fetching user info:', error);
        toast.error('Failed to fetch user information');
      }
    };

    fetchUserInfo();
  }, []);

  const handleLogout = useCallback(() => {
    logout();
    toast.success('You have been logged out');
    window.location.href = '/login';
  }, [logout]);

  // Prevent back navigation
  useEffect(() => {
    const preventBackNavigation = (event: PopStateEvent) => {
      window.history.pushState(null, '', window.location.href);
      event.preventDefault();
    };
    window.history.pushState(null, '', window.location.href);
    window.addEventListener('popstate', preventBackNavigation);

    return () => {
      window.removeEventListener('popstate', preventBackNavigation);
    };
  }, []);

  useEffect(() => {
    let idleTimer: NodeJS.Timeout;

    const resetTimer = () => {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        toast.error('You have been logged out due to inactivity');
        handleLogout();
      }, IDLE_TIMEOUT);
    };

    const events = ['mousemove', 'keydown', 'click', 'scroll'];
    events.forEach((event) => window.addEventListener(event, resetTimer));

    resetTimer();

    return () => {
      clearTimeout(idleTimer);
      events.forEach((event) => window.removeEventListener(event, resetTimer));
    };
  }, [handleLogout]);

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      <Header 
        userInfo={userInfo} 
        onLogout={handleLogout} 
        onUserManagement={() => {
          setShowUserManagement(true);
          toast.success('User Management opened');
        }}
      />
      <main className="flex-grow w-full px-4 py-8 overflow-y-auto">
        <div className="max-w-full mx-auto">
          {showUserManagement && userInfo?.is_superuser ? (
            <UserManagement />
          ) : (
            <>
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 className="text-xl font-semibold mb-4">Welcome to Bank Reconciliation</h2>
                <p className="text-gray-600">
                  This dashboard provides tools for bank reconciliation and process automation. Use the sections below to manage and monitor your automated processes.
                </p>
              </div>
              <ProcessTrigger />
              <ProcessLogs />
            </>
          )}
        </div>
      </main>
      <footer className="w-full bg-gray-200 text-center p-4 shadow-md">
        <p className="text-sm text-gray-600">© 2025 Axis Bank. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Dashboard;