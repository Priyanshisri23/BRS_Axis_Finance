'use client';

import React, { useMemo, useState } from 'react';
import {
  useTable,
  useSortBy,
  useGlobalFilter,
  usePagination,
  Column,
  Row,
  Cell,
  UseTableOptions,
  UseSortByOptions,
  UseGlobalFiltersOptions,
  UsePaginationOptions,
  TableInstance,
} from 'react-table';
import { User } from '../../types/Users';
import { Edit, Trash2, Search } from 'lucide-react';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import './UserTable.css';

interface UserTableProps {
  users: User[];
  isLoading: boolean;
  onEdit: (userId: number, isActive: boolean) => void;
  onDelete: (user: User) => void;
  loggedInUserId: number;
}

export const UserTable: React.FC<UserTableProps> = ({
  users,
  isLoading,
  onEdit,
  onDelete,
  loggedInUserId,
}) => {
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const data = useMemo(() => users, [users]);

  const columns = useMemo<Column<User>[]>(
    () => [
      {
        Header: 'Name',
        accessor: (row: User) => `${row.first_name} ${row.last_name}`,
      },
      {
        Header: 'Email',
        accessor: 'email',
      },
      {
        Header: 'Username',
        accessor: 'username',
      },
      {
        Header: 'Active',
        accessor: 'is_active',
        Cell: ({ value }: { value: boolean }) => (
          <span className={`status-indicator ${value ? 'active' : 'inactive'}`}>
            {value ? 'Active' : 'Inactive'}
          </span>
        ),
      },
      {
        Header: 'Super User',
        accessor: 'is_superuser',
        Cell: ({ value }: { value: boolean }) => (
          <span className={`status-indicator ${value ? 'superuser' : 'regular'}`}>
            {value ? 'Super User' : 'Regular User'}
          </span>
        ),
      },
      {
        Header: 'Created On',
        accessor: 'created_on',
        Cell: ({ value }: { value: string | null }) => <span>{value ? new Date(value).toLocaleString() : 'N/A'}</span>,
      },
      {
        Header: 'Updated On',
        accessor: 'updated_on',
        Cell: ({ value }: { value: string | null }) => <span>{value ? new Date(value).toLocaleString() : 'N/A'}</span>,
      },
      {
        Header: 'Actions',
        id: 'actions',
        Cell: ({ row }: { row: Row<User> }) => (
          <div className="action-buttons">
            <button 
              onClick={() => setEditingUser(row.original)} 
              className="edit-button" 
              title="Edit user"
              disabled={row.original.id === loggedInUserId}
            >
              <Edit size={16} />
            </button>
            <button
              onClick={() => onDelete(row.original)}
              className="delete-button"
              disabled={row.original.id === loggedInUserId}
              title={row.original.id === loggedInUserId ? "Can't delete your own account" : "Delete user"}
            >
              <Trash2 size={16} />
            </button>
          </div>
        ),
      },
    ],
    [onDelete, loggedInUserId]
  );

  const tableInstance = useTable(
    {
      columns,
      data,
      initialState: { pageIndex: 0, pageSize: 10 },
    } as UseTableOptions<User> & UseSortByOptions<User> & UseGlobalFiltersOptions<User> & UsePaginationOptions<User>,
    useGlobalFilter,
    useSortBy,
    usePagination
  ) as TableInstance<User> & {
    page: Row<User>[];
    setGlobalFilter: (filterValue: string) => void;
    nextPage: () => void;
    previousPage: () => void;
    canNextPage: boolean;
    canPreviousPage: boolean;
    pageOptions: number[];
    gotoPage: (page: number) => void;
    pageCount: number;
    setPageSize: (size: number) => void;
  };

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    state,
    setGlobalFilter,
    nextPage,
    previousPage,
    canNextPage,
    canPreviousPage,
    pageOptions,
    gotoPage,
    pageCount,
    setPageSize,
  } = tableInstance;

  const { globalFilter, pageIndex, pageSize } = state as {
    globalFilter: string;
    pageIndex: number;
    pageSize: number;
  };

  const handleStatusChange = (checked: boolean) => {
    if (editingUser) {
      onEdit(editingUser.id, checked);
      setEditingUser(null);
    }
  };

  return (
    <div className="user-table-container">
      <div className="search-container">
        <Search className="search-icon" size={20} />
        <input
          value={globalFilter || ''}
          onChange={e => setGlobalFilter(e.target.value)}
          placeholder="Search users..."
          className="search-input"
        />
      </div>
      <div className="table-wrapper">
        <table {...getTableProps()} className="user-table">
          <thead>
            {headerGroups.map((headerGroup, index) => (
              <tr {...headerGroup.getHeaderGroupProps()} key={index}>
                {headerGroup.headers.map((column, columnIndex) => (
                  <th {...column.getHeaderProps((column as any).getSortByToggleProps())} key={columnIndex}>
                    {column.render('Header')}
                    <span>
                      {(column as any).isSorted
                        ? (column as any).isSortedDesc
                          ? ' 🔽'
                          : ' 🔼'
                        : ''}
                    </span>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody {...getTableBodyProps()}>
            {isLoading ? (
              <tr>
                <td colSpan={10} className="loading-cell">Loading...</td>
              </tr>
            ) : page.length === 0 ? (
              <tr>
                <td colSpan={10} className="no-results-cell">No users found</td>
              </tr>
            ) : (
              page.map((row: Row<User>) => {
                prepareRow(row);
                return (
                  <tr {...row.getRowProps()} className="user-row" key={row.original.id}>
                    {row.cells.map((cell: Cell<User>, cellIndex) => (
                      <td {...cell.getCellProps()} key={cellIndex}>{cell.render('Cell')}</td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      <div className="pagination-container">
        <div className="pagination-info">
          Page{' '}
          <strong>
            {pageIndex + 1} of {pageOptions.length}
          </strong>{' '}
        </div>
        <div className="pagination-buttons">
          <button onClick={() => gotoPage(0)} disabled={!canPreviousPage} className="pagination-button">
            {'<<'}
          </button>
          <button onClick={() => previousPage()} disabled={!canPreviousPage} className="pagination-button">
            {'<'}
          </button>
          <button onClick={() => nextPage()} disabled={!canNextPage} className="pagination-button">
            {'>'}
          </button>
          <button onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage} className="pagination-button">
            {'>>'}
          </button>
        </div>
        <select
          value={pageSize}
          onChange={e => {
            setPageSize(Number(e.target.value));
          }}
          className="pagination-select"
        >
          {[10, 20, 30, 40, 50].map(pageSize => (
            <option key={pageSize} value={pageSize}>
              Show {pageSize}
            </option>
          ))}
        </select>
      </div>

      {editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
            <h2 className="text-xl font-bold mb-4 text-[#6e0f3b]">Update User Status</h2>
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`user-active-${editingUser.id}`}
                checked={editingUser.is_active}
                onCheckedChange={handleStatusChange}
              />
              <label htmlFor={`user-active-${editingUser.id}`} className="text-sm font-medium">
                Active
              </label>
            </div>
            <div className="mt-6 flex justify-end">
              <Button 
                variant="outline" 
                onClick={() => setEditingUser(null)}
                className="text-[#6e0f3b] border-[#6e0f3b] hover:bg-[#6e0f3b] hover:text-white"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserTable;