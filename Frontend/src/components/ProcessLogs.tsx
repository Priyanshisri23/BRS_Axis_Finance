import React, { useState, useEffect, useMemo } from 'react';
import { Eye, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, ArrowUpDown } from 'lucide-react';
import { getLogs } from '../services/logs';
import LogDetailsModal from './LogDetailsModal';
import DownloadLogsExcel from './DownloadLogsExcel';

interface LogEntry {
  id: number;
  processName: string;
  startedAt: string;
  completedAt: string | null;
  result: 'Success' | 'Failure' | 'Pending';
  timeTaken: string;
  userFullName: string;
  date: string;
  details: string;
}

interface SortConfig {
  key: keyof LogEntry;
  direction: 'asc' | 'desc';
}

const ProcessLogs: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [logsPerPage] = useState(10);
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'date', direction: 'desc' });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogsWithDelay = () => {
      setTimeout(() => {
        fetchLogs();
      }, 2000); // 2-second delay
    };

    fetchLogsWithDelay();
  }, []);

  const fetchLogs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getLogs();
      const formattedLogs = response.data.map((log: any) => {
        const startTime = new Date(log.start_time);
        const endTime = log.end_time ? new Date(log.end_time) : null;

        const formattedDate = !isNaN(startTime.getTime())
          ? `${startTime.getDate().toString().padStart(2, '0')}-${(startTime.getMonth() + 1)
              .toString()
              .padStart(2, '0')}-${startTime.getFullYear()}`
          : 'Invalid Date';

        const formattedStartTime = !isNaN(startTime.getTime())
          ? startTime.toLocaleTimeString('en-US', { hour12: true })
          : 'Invalid Date';
        
        const formattedEndTime = endTime && !isNaN(endTime.getTime())
          ? endTime.toLocaleTimeString('en-US', { hour12: true })
          : 'N/A';

        const timeTaken = log.time_taken || 'N/A';

        return {
          id: log.id,
          processName: log.process_name,
          startedAt: formattedStartTime,
          completedAt: formattedEndTime,
          result: log.result,
          timeTaken,
          userFullName: log.user_full_name || 'Unknown User',
          date: formattedDate,
          details: log.details || 'No additional details provided',
        };
      });
      setLogs(formattedLogs);
    } catch (error) {
      console.error('Error fetching logs:', error);
      setError('Failed to fetch logs. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const openModal = (log: LogEntry) => {
    setSelectedLog(log);
    setIsModalOpen(true);
  };

  const sortedLogs = useMemo(() => {
    const sortableItems = [...logs];
    sortableItems.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue == null && bValue == null) return 0;
      if (aValue == null) return sortConfig.direction === 'asc' ? -1 : 1;
      if (bValue == null) return sortConfig.direction === 'asc' ? 1 : -1;
      
      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
    return sortableItems;
  }, [logs, sortConfig]);

  const requestSort = (key: keyof LogEntry) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const indexOfLastLog = currentPage * logsPerPage;
  const indexOfFirstLog = indexOfLastLog - logsPerPage;
  const currentLogs = sortedLogs.slice(indexOfFirstLog, indexOfLastLog);

  const paginate = (pageNumber: number) => setCurrentPage(pageNumber);

  const totalPages = Math.ceil(logs.length / logsPerPage);

  const tableHeaders: (keyof LogEntry)[] = ['date', 'processName', 'startedAt', 'completedAt', 'result', 'timeTaken', 'userFullName'];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-[#6e0f3b]"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600 p-4">
        <p>{error}</p>
        <button 
          onClick={fetchLogs} 
          className="mt-4 bg-[#6e0f3b] text-white px-4 py-2 rounded hover:bg-[#8a1149]"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg p-6 w-full">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-[#6e0f3b] mb-2">Process Logs</h2>
          <p className="text-gray-600">View the history of automated processes.</p>
        </div>
        <DownloadLogsExcel />
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              {tableHeaders.map((key) => (
                <th 
                  key={key}
                  className="py-2 px-4 border-b text-left cursor-pointer hover:bg-gray-200"
                  onClick={() => requestSort(key)}
                >
                  <div className="flex items-center">
                    {key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}
                    <ArrowUpDown className="ml-1 h-4 w-4" />
                  </div>
                </th>
              ))}
              <th className="py-2 px-4 border-b text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentLogs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{log.date}</td>
                <td className="py-2 px-4 border-b">{log.processName}</td>
                <td className="py-2 px-4 border-b">{log.startedAt}</td>
                <td className="py-2 px-4 border-b">{log.completedAt}</td>
                <td className="py-2 px-4 border-b">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    log.result === 'Success' ? 'bg-green-100 text-green-800' 
                    : log.result === 'Failure' ? 'bg-red-100 text-red-800' 
                    : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {log.result}
                  </span>
                </td>
                <td className="py-2 px-4 border-b">{log.timeTaken}</td>
                <td className="py-2 px-4 border-b">{log.userFullName}</td>
                <td className="py-2 px-4 border-b">
                  <button
                    onClick={() => openModal(log)}
                    className="text-[#6e0f3b] hover:text-[#8a1149] focus:outline-none"
                    aria-label="View details"
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-700">
            Showing <span className="font-medium">{indexOfFirstLog + 1}</span> to <span className="font-medium">{Math.min(indexOfLastLog, logs.length)}</span> of{' '}
            <span className="font-medium">{logs.length}</span> results
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => paginate(1)}
            disabled={currentPage === 1}
            className="px-2 py-1 border rounded text-sm disabled:opacity-50"
          >
            <ChevronsLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-2 py-1 border rounded text-sm disabled:opacity-50"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="px-4 py-1 border rounded bg-gray-100">
            {currentPage} / {totalPages}
          </span>
          <button
            onClick={() => paginate(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-2 py-1 border rounded text-sm disabled:opacity-50"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
          <button
            onClick={() => paginate(totalPages)}
            disabled={currentPage === totalPages}
            className="px-2 py-1 border rounded text-sm disabled:opacity-50"
          >
            <ChevronsRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {selectedLog && (
        <LogDetailsModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          log={selectedLog}
        />
      )}
    </div>
  );
};

export default ProcessLogs;