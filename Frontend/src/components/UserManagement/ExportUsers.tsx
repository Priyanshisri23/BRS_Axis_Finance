import React from 'react';
import * as XLSX from 'xlsx';
import { Download } from 'lucide-react';
import { User } from '../../types/Users';

interface ExportUsersProps {
  users: User[];
}

const ExportUsers: React.FC<ExportUsersProps> = ({ users }) => {
  const exportToExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(
      users.map(user => ({
        'User ID': user.id,
        'Name': `${user.first_name} ${user.last_name}`,
        'Email': user.email,
        'Username': user.username,
        'Active': user.is_active ? 'Yes' : 'No',
        'Superuser': user.is_superuser ? 'Yes' : 'No',
        'Created On': user.created_on ? new Date(user.created_on).toLocaleString() : 'N/A',
        'Updated On': user.updated_on ? new Date(user.updated_on).toLocaleString() : 'N/A'
      }))
    );

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Users');

    // Generate buffer
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });

    // Convert to Blob
    const data = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    // Create download link
    const url = window.URL.createObjectURL(data);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'users_export.xlsx';
    
    // Trigger download
    link.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={exportToExcel}
      className="bg-[#6e0f3b] hover:bg-[#8a1149] text-white font-bold py-2 px-4 rounded flex items-center transition-colors"
    >
      <Download className="mr-2" size={16} />
      Export Users
    </button>
  );
};

export default ExportUsers;