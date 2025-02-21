import React from 'react';
import { X } from 'lucide-react';
import moment from 'moment';

interface LogEntry {
  id: number;
  processName: string;
  startedAt: string;
  completedAt: string | null;  // Allow null for completedAt
  result: 'Success' | 'Failure' | 'Pending';
  timeTaken: string;
  userFullName: string;
  details: string;
}

interface LogDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  log: LogEntry;
}

const LogDetailsModal: React.FC<LogDetailsModalProps> = ({ isOpen, onClose, log }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-[#6e0f3b]">Log Details</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-lg">Process</h3>
            <p>{log.processName}</p>
          </div>
          <div>
            <h3 className="font-semibold text-lg">Started At</h3>
            <p>{moment(log.startedAt, 'HH:mm:ss A').format('HH:mm:ss A')}</p>
          </div>
          <div>
            <h3 className="font-semibold text-lg">Completed At</h3>
            <p>{log.completedAt ? moment(log.completedAt, 'HH:mm:ss A').format('HH:mm:ss A') : 'N/A'}</p> {/* Handle null */}
          </div>
          <div>
            <h3 className="font-semibold text-lg">Result</h3>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              log.result === 'Success' ? 'bg-green-100 text-green-800' : 
              log.result === 'Failure' ? 'bg-red-100 text-red-800' : 
              'bg-yellow-100 text-yellow-800'
            }`}>
              {log.result}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-lg">Time Taken</h3>
            <p>{log.timeTaken}</p>
          </div>
          <div>
            <h3 className="font-semibold text-lg">User</h3>
            <p>{log.userFullName}</p>
          </div>
          <div>
            <h3 className="font-semibold text-lg">Details</h3>
            <p>{log.details}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogDetailsModal;
