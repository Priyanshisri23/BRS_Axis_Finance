import React, { useState, useEffect } from 'react';
import { ClockIcon, CheckCircleIcon, XCircleIcon, PlayIcon } from 'lucide-react';
import api from '../services/api';

interface Process {
  id: number;
  name: string;
  description: string;
  endpoint: string;
  status: 'Idle' | 'Running' | 'Completed' | 'Failed';
  startedAt: string | null;
  completedAt: string | null;
}

const initialProcesses: Process[] = [
  { id: 1, name: 'BRS - Account 607', description: 'BRS Process - Account 607', endpoint: '/process/account_607', status: 'Idle', startedAt: null, completedAt: null },
  { id: 2, name: 'BRS - Account 669', description: 'BRS Process - Account 669', endpoint: '/process/account_669', status: 'Idle', startedAt: null, completedAt: null },
  { id: 3, name: 'BRS - Account 7687', description: 'BRS Process - Account 7687', endpoint: '/process/account_7687', status: 'Idle', startedAt: null, completedAt: null },
  { id: 4, name: 'BRS - Account 8350', description: 'BRS Process - Account 8350', endpoint: '/process/account_8350', status: 'Idle', startedAt: null, completedAt: null },
  { id: 5, name: 'BRS - Account 9197', description: 'BRS Process - Account 9197', endpoint: '/process/account_9197', status: 'Idle', startedAt: null, completedAt: null },
  { id: 6, name: 'BRS - Account 86033', description: 'BRS Process - Account 86033', endpoint: '/process/account_86033', status: 'Idle', startedAt: null, completedAt: null }
  // { id: 7, name: 'Test Bot', description: 'For testing purpose', endpoint: '/bot/bot1', status: 'Idle', startedAt: null, completedAt: null }
]

const ProcessTrigger: React.FC = () => {
  const [processes, setProcesses] = useState<Process[]>(initialProcesses);
  const [isProcessRunning, setIsProcessRunning] = useState(false);

  // Add a listener for the beforeunload event
  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (isProcessRunning) {
        event.preventDefault();
        event.returnValue = 'A process is currently running. Are you sure you want to leave?';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isProcessRunning]);

  const runProcess = async (process: Process) => {
    setIsProcessRunning(true); // Mark that a process is running
    try {
      setProcesses(prevProcesses =>
        prevProcesses.map(p =>
          p.id === process.id ? { ...p, status: 'Running', startedAt: new Date().toISOString(), completedAt: null } : p
        )
      );

      const response = await api.post(process.endpoint);

      setProcesses(prevProcesses =>
        prevProcesses.map(p =>
          p.id === process.id ? { ...p, status: response.data.success ? 'Completed' : 'Failed', completedAt: new Date().toISOString() } : p
        )
      );
    } catch (error) {
      console.error(`Error running process ${process.id}:`, error);
      setProcesses(prevProcesses =>
        prevProcesses.map(p =>
          p.id === process.id ? { ...p, status: 'Failed', completedAt: new Date().toISOString() } : p
        )
      );
    } finally {
      setIsProcessRunning(false); // Mark that the process has stopped running
    }
  };

  const getStatusIcon = (status: Process['status']) => {
    switch (status) {
      case 'Idle': return <ClockIcon className="w-5 h-5 text-gray-500" />;
      case 'Running': return <ClockIcon className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'Completed': return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'Failed': return <XCircleIcon className="w-5 h-5 text-red-500" />;
    }
  };

  const calculateTimeTaken = (startedAt: string | null, completedAt: string | null) => {
    if (!startedAt || !completedAt) return 'N/A';
    const startTime = new Date(startedAt).getTime();
    const endTime = new Date(completedAt).getTime();
    const timeTaken = Math.round((endTime - startTime) / 1000); // Time in seconds
    const minutes = Math.floor(timeTaken / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) return `${hours}h ${minutes % 60}m ${timeTaken % 60}s`;
    if (minutes > 0) return `${minutes}m ${timeTaken % 60}s`;
    return `${timeTaken}s`;
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6 w-full mb-8">
      <h2 className="text-2xl font-bold text-[#6e0f3b] mb-2">Automation Processes</h2>
      <p className="text-gray-600 mb-6">Trigger automation processes from this dashboard.</p>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="py-2 px-4 border-b text-left">Process Name</th>
              <th className="py-2 px-4 border-b text-left">Description</th>
              <th className="py-2 px-4 border-b text-left">Endpoint</th>
              <th className="py-2 px-4 border-b text-left">Started At</th>
              <th className="py-2 px-4 border-b text-left">Status</th>
              <th className="py-2 px-4 border-b text-left">Time Taken</th>
              <th className="py-2 px-4 border-b text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {processes.map((process) => (
              <tr key={process.id} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b font-semibold">{process.name}</td>
                <td className="py-2 px-4 border-b">{process.description}</td>
                <td className="py-2 px-4 border-b">{process.endpoint}</td>
                <td className="py-2 px-4 border-b">{process.startedAt ? new Date(process.startedAt).toLocaleString() : '-'}</td>
                <td className="py-2 px-4 border-b">
                  <div className="flex items-center">
                    {getStatusIcon(process.status)}
                    <span className="ml-2">{process.status}</span>
                  </div>
                </td>
                <td className="py-2 px-4 border-b">{calculateTimeTaken(process.startedAt, process.completedAt)}</td>
                <td className="py-2 px-4 border-b">
                  <button
                    onClick={() => runProcess(process)}
                    disabled={process.status === 'Running'}
                    className="bg-[#6e0f3b] text-white px-4 py-2 rounded-md hover:bg-[#8a1149] focus:outline-none focus:ring-2 focus:ring-[#6e0f3b] focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    <PlayIcon className="w-4 h-4 mr-2" />
                    Run
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ProcessTrigger;
