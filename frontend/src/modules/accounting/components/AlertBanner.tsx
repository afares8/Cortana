import React from 'react';
import { AlertTriangle, Check } from 'lucide-react';
import { Obligation } from '../types';

interface AlertBannerProps {
  upcoming: Obligation[];
  overdue: Obligation[];
  isLoading?: boolean;
}

const AlertBanner: React.FC<AlertBannerProps> = ({ upcoming, overdue, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="bg-gray-50 text-gray-700 p-4 rounded-md mb-6 flex items-center">
        <span>Loading alerts...</span>
      </div>
    );
  }

  if (upcoming.length === 0 && overdue.length === 0) {
    return (
      <div className="bg-green-50 text-green-700 p-4 rounded-md mb-6 flex items-center">
        <Check className="h-5 w-5 mr-2" />
        <span>No upcoming or overdue obligations at this time.</span>
      </div>
    );
  }

  return (
    <div className="mb-6">
      {overdue.length > 0 && (
        <div className="bg-red-50 text-red-700 p-4 rounded-md mb-2 flex flex-col">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            <span className="font-semibold">You have {overdue.length} overdue obligation(s)!</span>
          </div>
          <ul className="mt-2 ml-7 list-disc">
            {overdue.slice(0, 3).map((obligation) => (
              <li key={obligation.id}>
                {obligation.name} for {obligation.company_name || 'Unknown Company'} - Due on {new Date(obligation.next_due_date).toLocaleDateString()}
              </li>
            ))}
            {overdue.length > 3 && (
              <li>And {overdue.length - 3} more...</li>
            )}
          </ul>
        </div>
      )}

      {upcoming.length > 0 && (
        <div className="bg-yellow-50 text-yellow-700 p-4 rounded-md flex flex-col">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            <span className="font-semibold">You have {upcoming.length} upcoming obligation(s) within reminder period!</span>
          </div>
          <ul className="mt-2 ml-7 list-disc">
            {upcoming.slice(0, 3).map((obligation) => (
              <li key={obligation.id}>
                {obligation.name} for {obligation.company_name || 'Unknown Company'} - Due on {new Date(obligation.next_due_date).toLocaleDateString()}
              </li>
            ))}
            {upcoming.length > 3 && (
              <li>And {upcoming.length - 3} more...</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AlertBanner;
