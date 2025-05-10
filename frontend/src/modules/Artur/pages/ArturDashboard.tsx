import React, { useState, useEffect } from 'react';
import { Brain, AlertTriangle, CheckCircle } from 'lucide-react';
import { getDepartmentHealth } from '../api/arturApi';
import { DepartmentHealth } from '../types';

const ArturDashboard: React.FC = () => {
  const [departmentHealth, setDepartmentHealth] = useState<DepartmentHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDepartmentHealth = async () => {
      try {
        setLoading(true);
        const data = await getDepartmentHealth();
        setDepartmentHealth(data);
        setError(null);
      } catch (err) {
        setError('Failed to load department health data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDepartmentHealth();
  }, []);

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <Brain className="h-8 w-8 mr-3 text-blue-600" />
          <h1 className="text-2xl font-bold">Artur Dashboard</h1>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Brain className="h-6 w-6 mr-2 text-blue-600" />
                <h2 className="text-lg font-semibold">System Health</h2>
              </div>
              <div className="text-3xl font-bold text-blue-600">
                {departmentHealth.length > 0
                  ? Math.round(
                      departmentHealth.reduce((acc, dept) => acc + dept.health_score, 0) /
                        departmentHealth.length
                    )
                  : 'N/A'}
                %
              </div>
              <p className="text-gray-600 mt-2">Overall system health score</p>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="flex items-center mb-4">
                <AlertTriangle className="h-6 w-6 mr-2 text-yellow-600" />
                <h2 className="text-lg font-semibold">Active Suggestions</h2>
              </div>
              <div className="text-3xl font-bold text-yellow-600">
                {departmentHealth.reduce((acc, dept) => acc + dept.active_suggestions, 0)}
              </div>
              <p className="text-gray-600 mt-2">Pending improvement suggestions</p>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <div className="flex items-center mb-4">
                <CheckCircle className="h-6 w-6 mr-2 text-green-600" />
                <h2 className="text-lg font-semibold">Recent Interventions</h2>
              </div>
              <div className="text-3xl font-bold text-green-600">
                {departmentHealth.reduce((acc, dept) => acc + dept.recent_interventions, 0)}
              </div>
              <p className="text-gray-600 mt-2">Successful system improvements</p>
            </div>
          </div>

          <h2 className="text-xl font-semibold mb-4">Department Health Map</h2>
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Health Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Active Suggestions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recent Interventions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {departmentHealth.map((dept) => (
                  <tr key={dept.department_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {dept.department_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div
                          className={`${getHealthColor(
                            dept.health_score
                          )} h-3 w-3 rounded-full mr-2`}
                        ></div>
                        <div className="text-sm text-gray-900">{dept.health_score}%</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{dept.active_suggestions}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{dept.recent_interventions}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default ArturDashboard;
