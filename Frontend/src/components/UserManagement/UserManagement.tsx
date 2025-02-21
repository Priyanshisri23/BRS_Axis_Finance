'use client';

import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Home } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getUsers, updateUserStatus, deleteUser } from '../../services/userManagementService';
import { UserTable } from './UserTable';
import ExportUsers from './ExportUsers';
import { User } from '../../types/Users';

export const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loggedInUserId] = useState<number>(1); // This should be replaced with the actual logged-in user's ID
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; user: User | null; inputName: string }>({
    isOpen: false,
    user: null,
    inputName: '',
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedUsers = await getUsers();
      setUsers(fetchedUsers);
    } catch (err) {
      setError('Failed to fetch users. Please try again.');
      toast.error('Failed to fetch users');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateUserStatus = async (userId: number, isActive: boolean) => {
    try {
      const response = await updateUserStatus(userId, isActive);
      toast.success(response.message);
      fetchUsers();
    } catch (err) {
      toast.error('Failed to update user status');
    }
  };

  const handleDeleteUser = async (user: User) => {
    if (user.id === loggedInUserId) {
      toast.error("You cannot delete your own account.");
      return;
    }

    setDeleteConfirmation({ isOpen: true, user, inputName: '' });
  };

  const confirmDeleteUser = async () => {
    const { user, inputName } = deleteConfirmation;
    if (!user) return;

    if (inputName.toLowerCase() !== user.username.toLowerCase()) {
      toast.error("The entered username doesn't match. Deletion cancelled.");
      return;
    }

    try {
      await deleteUser(user.id);
      toast.success('User deleted successfully');
      fetchUsers();
      setDeleteConfirmation({ isOpen: false, user: null, inputName: '' });
    } catch (err) {
      toast.error('Failed to delete user');
    }
  };

  const handleEditUser = (userId: number, isActive: boolean) => {
    handleUpdateUserStatus(userId, isActive);
  };

  return (
    <div className="px-4 mt-6">
      <div className="flex justify-between items-center mb-6 max-w-[1920px] mx-auto">
        <h2 className="text-3xl font-bold text-[#6e0f3b]">User Management</h2>
        <div className="flex items-center space-x-4">
          <Link 
            to="/" 
            className="bg-[#6e0f3b] hover:bg-[#8a1149] text-white font-medium py-2 px-4 rounded-md flex items-center transition-colors"
          >
            <Home className="mr-2" size={16} />
            Home
          </Link>
          <ExportUsers users={users} />
        </div>
      </div>

      {error && <div className="text-red-500 mb-4">{error}</div>}

      <UserTable
        users={users}
        isLoading={isLoading}
        onEdit={handleEditUser}
        onDelete={handleDeleteUser}
        loggedInUserId={loggedInUserId}
      />

      {deleteConfirmation.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
            <h3 className="text-xl font-bold mb-4 text-[#6e0f3b]">Confirm User Deletion</h3>
            <p className="mb-4 text-gray-600">
              Are you sure you want to delete the user "{deleteConfirmation.user?.username}"? This action cannot be undone.
            </p>
            <p className="mb-2 text-sm text-gray-500">To confirm, please type the username below:</p>
            <input
              type="text"
              value={deleteConfirmation.inputName}
              onChange={(e) => setDeleteConfirmation(prev => ({ ...prev, inputName: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#6e0f3b] focus:border-transparent"
              placeholder="Enter username"
            />
            <div className="flex justify-end space-x-4 mt-6">
              <button 
                onClick={() => setDeleteConfirmation({ isOpen: false, user: null, inputName: '' })}
                className="px-4 py-2 text-[#6e0f3b] border border-[#6e0f3b] rounded hover:bg-[#6e0f3b] hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={confirmDeleteUser}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Delete User
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;