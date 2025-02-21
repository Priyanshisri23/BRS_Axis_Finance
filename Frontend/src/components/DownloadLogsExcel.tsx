import React from 'react';
import * as XLSX from 'xlsx';
import { Download } from 'lucide-react';
import { getLogs } from '../services/logs';

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

interface ExcelRow {
  Date: string;
  Process: string;
  'Started At': string;
  'Completed At': string | null;
  Result: 'Success' | 'Failure' | 'Pending';
  'Time Taken': string;
  User: string;
  Details: string;
}

export default function DownloadLogsExcel() {
  const handleDownload = async () => {
    try {
      const response = await getLogs();
      const logs: LogEntry[] = response.data.map((log: any) => {
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

      const excelData: ExcelRow[] = logs.map(log => ({
        Date: log.date,
        Process: log.processName,
        'Started At': log.startedAt,
        'Completed At': log.completedAt,
        Result: log.result,
        'Time Taken': log.timeTaken,
        User: log.userFullName,
        Details: log.details
      }));

      const worksheet = XLSX.utils.json_to_sheet(excelData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, "Process Logs");

      // Style the header
      const headerStyle = {
        font: { bold: true, color: { rgb: "FFFFFF" }, sz: 12 },
        fill: { fgColor: { rgb: "4472C4" } },
        border: {
          top: { style: 'thin', color: { rgb: '000000' } },
          bottom: { style: 'thin', color: { rgb: '000000' } },
          left: { style: 'thin', color: { rgb: '000000' } },
          right: { style: 'thin', color: { rgb: '000000' } }
        }
      };

      // Apply styles to all cells
      const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1');
      for (let R = range.s.r; R <= range.e.r; ++R) {
        for (let C = range.s.c; C <= range.e.c; ++C) {
          const cellAddress = XLSX.utils.encode_cell({ r: R, c: C });
          if (!worksheet[cellAddress]) worksheet[cellAddress] = { v: '', t: 's' };
          worksheet[cellAddress].s = {
            border: {
              top: { style: 'thin', color: { rgb: '000000' } },
              bottom: { style: 'thin', color: { rgb: '000000' } },
              left: { style: 'thin', color: { rgb: '000000' } },
              right: { style: 'thin', color: { rgb: '000000' } }
            }
          };
          if (R === 0) {
            worksheet[cellAddress].s = { ...worksheet[cellAddress].s, ...headerStyle };
          }
        }
      }

      worksheet['!rows'] = [{ hpt: 20 }]; // Set the height of the first row (header) to 20 points

      // Auto-size columns
      const maxWidths: { [key: number]: number } = excelData.reduce((acc, row) => {
        (Object.keys(row) as Array<keyof ExcelRow>).forEach((key, index) => {
          const cellValue = row[key] ? row[key]!.toString() : '';
          acc[index] = Math.max(acc[index] || 0, cellValue.length);
        });
        return acc;
      }, {} as { [key: number]: number });

      worksheet['!cols'] = Object.keys(maxWidths).map(key => ({ wch: Math.min(maxWidths[Number(key)] + 2, 50) }));

      XLSX.writeFile(workbook, "Axis_Bank_Process_Logs.xlsx");
    } catch (error) {
      console.error('Error downloading logs:', error);
      alert('Failed to download logs. Please try again.');
    }
  };

  return (
    <button
      onClick={handleDownload}
      className="bg-[#6e0f3b] hover:bg-[#8a1149] text-white font-bold py-2 px-4 rounded inline-flex items-center"
    >
      <Download className="mr-2" size={16} />
      Download Logs
    </button>
  );
}