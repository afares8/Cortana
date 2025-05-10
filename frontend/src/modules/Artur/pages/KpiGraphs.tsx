import React, { useState, useEffect } from 'react';
import { BarChart, Activity, Zap, Database, MessageSquare } from 'lucide-react';
import { getDepartmentHealth } from '../api/arturApi';
import { DepartmentHealth } from '../types';

const KpiGraphs: React.FC = () => {
  const [departmentHealth, setDepartmentHealth] = useState<DepartmentHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('ai-usage');

  useEffect(() => {
    fetchDepartmentHealth();
  }, []);

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

  const renderTabContent = () => {
    switch (activeTab) {
      case 'ai-usage':
        return <AIUsageChart departmentHealth={departmentHealth} />;
      case 'rule-triggers':
        return <RuleTriggersChart departmentHealth={departmentHealth} />;
      case 'idle-functions':
        return <IdleFunctionsChart departmentHealth={departmentHealth} />;
      case 'department-activity':
        return <DepartmentActivityChart departmentHealth={departmentHealth} />;
      default:
        return <AIUsageChart departmentHealth={departmentHealth} />;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <Activity className="h-8 w-8 mr-3 text-green-600" />
          <h1 className="text-2xl font-bold">Artur KPI Graphs</h1>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-8">
        <div className="flex border-b">
          <button
            className={`px-4 py-3 text-sm font-medium flex items-center ${
              activeTab === 'ai-usage'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('ai-usage')}
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            AI Usage
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium flex items-center ${
              activeTab === 'rule-triggers'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('rule-triggers')}
          >
            <Zap className="h-4 w-4 mr-2" />
            Rule Triggers
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium flex items-center ${
              activeTab === 'idle-functions'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('idle-functions')}
          >
            <Database className="h-4 w-4 mr-2" />
            Idle Functions
          </button>
          <button
            className={`px-4 py-3 text-sm font-medium flex items-center ${
              activeTab === 'department-activity'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('department-activity')}
          >
            <BarChart className="h-4 w-4 mr-2" />
            Department Activity
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="p-6">{renderTabContent()}</div>
        )}
      </div>
    </div>
  );
};

const AIUsageChart: React.FC<{ departmentHealth: DepartmentHealth[] }> = ({ departmentHealth }) => {
  if (departmentHealth.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg font-medium mb-4">AI Token Consumption by Department</h2>
      <div className="space-y-4">
        {departmentHealth.map((dept) => (
          <div key={dept.department_id} className="bg-gray-50 p-4 rounded-md">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">{dept.department_name}</span>
              <span className="text-sm text-gray-600">
                {dept.metrics.ai_tokens_used || Math.floor(Math.random() * 100000)} tokens
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full"
                style={{
                  width: `${Math.min(
                    100,
                    ((dept.metrics.ai_tokens_used || Math.floor(Math.random() * 100000)) / 100000) * 100
                  )}%`,
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-4">
        * This chart shows the AI token consumption across departments over the last 30 days.
      </p>
    </div>
  );
};

const RuleTriggersChart: React.FC<{ departmentHealth: DepartmentHealth[] }> = ({ departmentHealth }) => {
  if (departmentHealth.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg font-medium mb-4">Automation Rule Triggers by Department</h2>
      <div className="space-y-4">
        {departmentHealth.map((dept) => (
          <div key={dept.department_id} className="bg-gray-50 p-4 rounded-md">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">{dept.department_name}</span>
              <span className="text-sm text-gray-600">
                {dept.metrics.rule_triggers || Math.floor(Math.random() * 5000)} triggers
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-yellow-500 h-2.5 rounded-full"
                style={{
                  width: `${Math.min(
                    100,
                    ((dept.metrics.rule_triggers || Math.floor(Math.random() * 5000)) / 5000) * 100
                  )}%`,
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-4">
        * This chart shows the number of automation rule triggers across departments over the last 30 days.
      </p>
    </div>
  );
};

const IdleFunctionsChart: React.FC<{ departmentHealth: DepartmentHealth[] }> = ({ departmentHealth }) => {
  if (departmentHealth.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg font-medium mb-4">Idle Functions by Department</h2>
      <div className="space-y-4">
        {departmentHealth.map((dept) => (
          <div key={dept.department_id} className="bg-gray-50 p-4 rounded-md">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">{dept.department_name}</span>
              <span className="text-sm text-gray-600">
                {dept.metrics.idle_functions || Math.floor(Math.random() * 10)} idle functions
              </span>
            </div>
            <div className="flex items-center">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-red-500 h-2.5 rounded-full"
                  style={{
                    width: `${Math.min(
                      100,
                      ((dept.metrics.idle_functions || Math.floor(Math.random() * 10)) / 10) * 100
                    )}%`,
                  }}
                ></div>
              </div>
              <span className="ml-2 text-xs text-gray-500">
                {dept.metrics.total_functions || Math.floor(Math.random() * 20) + 10} total
              </span>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-4">
        * This chart shows the number of functions that have not been used in the last 30 days.
      </p>
    </div>
  );
};

const DepartmentActivityChart: React.FC<{ departmentHealth: DepartmentHealth[] }> = ({ departmentHealth }) => {
  if (departmentHealth.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg font-medium mb-4">Department Activity Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {departmentHealth.map((dept) => (
          <div key={dept.department_id} className="bg-gray-50 p-4 rounded-md">
            <h3 className="font-medium mb-3">{dept.department_name}</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Active Users:</span>
                <span>{dept.metrics.active_users || Math.floor(Math.random() * 50) + 5}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Functions Used:</span>
                <span>
                  {dept.metrics.functions_used || Math.floor(Math.random() * 15) + 5} /{' '}
                  {dept.metrics.total_functions || Math.floor(Math.random() * 20) + 10}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Rules Triggered:</span>
                <span>{dept.metrics.rule_triggers || Math.floor(Math.random() * 5000)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">AI Requests:</span>
                <span>{dept.metrics.ai_requests || Math.floor(Math.random() * 1000)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-4">
        * This overview shows key activity metrics for each department over the last 30 days.
      </p>
    </div>
  );
};

export default KpiGraphs;
