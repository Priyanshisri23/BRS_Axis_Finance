import React, { useState } from 'react';
import DropdownMenu, { DropdownMenuItem } from '../ui/dropdown-menu';
import { Settings } from 'lucide-react';
import { UpdatePasswordModal } from '../Auth/UpdatePasswordModal';

interface UserInfo {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface HeaderProps {
  userInfo: UserInfo | null;
  onLogout: () => void;
  onUserManagement: () => void;
}

const Header: React.FC<HeaderProps> = ({ userInfo, onLogout, onUserManagement }) => {
  const [showUpdatePasswordModal, setShowUpdatePasswordModal] = useState(false);

  return (
    <header className="bg-[#6e0f3b] text-white shadow-md">
      <div className="w-full px-4 py-4 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-xl font-semibold">Axis Finance </h1>
        </div>
        <div className="flex items-center space-x-4">
          {userInfo?.is_superuser && (
            <button
              onClick={onUserManagement}
              className="flex items-center px-3 py-2 bg-white text-[#6e0f3b] rounded hover:bg-gray-200 transition-colors"
            >
              <Settings className="w-5 h-5 mr-2" />
              Management
            </button>
          )}
          {userInfo && (
            <DropdownMenu>
              <DropdownMenu.Trigger asChild>
                <button className="flex items-center space-x-2 focus:outline-none bg-white text-[#6e0f3b] px-3 py-2 rounded hover:bg-gray-200 transition-colors">
                  <span>
                    {userInfo.first_name} {userInfo.last_name} 
                    <span className="ml-2 text-sm font-normal">
                      ({userInfo.is_superuser ? 'Superadmin' : 'User'})
                    </span>
                  </span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Content>
                {/* <DropdownMenuItem onSelect={() => setShowUpdatePasswordModal(true)}>
                  Update Password
                </DropdownMenuItem> */}
                <DropdownMenuItem onSelect={onLogout}>
                  Logout
                </DropdownMenuItem>
              </DropdownMenu.Content>
            </DropdownMenu>
          )}
        </div>
      </div>
      <UpdatePasswordModal
        isOpen={showUpdatePasswordModal}
        onClose={() => setShowUpdatePasswordModal(false)}
      />
    </header>
  );
};

export default Header;