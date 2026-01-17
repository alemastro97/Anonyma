import React from 'react';

const Jobs: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Jobs</h2>
        <p className="mt-2 text-sm text-gray-600">
          View and manage your anonymization jobs
        </p>
      </div>

      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs yet</h3>
        <p className="mt-1 text-sm text-gray-500">
          Process a document to see job history here
        </p>
      </div>
    </div>
  );
};

export default Jobs;
