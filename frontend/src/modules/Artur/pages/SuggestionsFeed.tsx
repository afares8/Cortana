import React, { useState, useEffect } from 'react';
import { Lightbulb, Play, Check, X } from 'lucide-react';
import { getSuggestions, updateSuggestionStatus, runEvaluationCycle } from '../api/arturApi';
import { ArturSuggestion, SuggestionStatus } from '../types';

const SuggestionsFeed: React.FC = () => {
  const [suggestions, setSuggestions] = useState<ArturSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runningEvaluation, setRunningEvaluation] = useState(false);

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      const data = await getSuggestions();
      setSuggestions(data);
      setError(null);
    } catch (err) {
      setError('Failed to load suggestions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (id: number, status: string) => {
    try {
      await updateSuggestionStatus(id, status);
      setSuggestions(
        suggestions.map((suggestion) =>
          suggestion.id === id ? { ...suggestion, status } : suggestion
        )
      );
    } catch (err) {
      setError('Failed to update suggestion status');
      console.error(err);
    }
  };

  const handleRunEvaluation = async () => {
    try {
      setRunningEvaluation(true);
      await runEvaluationCycle();
      await fetchSuggestions();
    } catch (err) {
      setError('Failed to run evaluation cycle');
      console.error(err);
    } finally {
      setRunningEvaluation(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case SuggestionStatus.APPROVED:
        return 'bg-green-100 text-green-800';
      case SuggestionStatus.EXECUTED:
        return 'bg-blue-100 text-blue-800';
      case SuggestionStatus.IGNORED:
        return 'bg-gray-100 text-gray-800';
      case SuggestionStatus.SIMULATED:
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <Lightbulb className="h-8 w-8 mr-3 text-yellow-500" />
          <h1 className="text-2xl font-bold">Artur Suggestions</h1>
        </div>
        <button
          onClick={handleRunEvaluation}
          disabled={runningEvaluation}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {runningEvaluation ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
              Running...
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              Run Evaluation Cycle
            </>
          )}
        </button>
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
      ) : suggestions.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <Lightbulb className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No suggestions yet</h3>
          <p className="text-gray-600">
            Artur hasn't generated any improvement suggestions yet. Run an evaluation cycle to analyze your system.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {suggestions.map((suggestion) => (
            <div key={suggestion.id} className="bg-white shadow-md rounded-lg overflow-hidden">
              <div className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center mb-2">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mr-2 ${getStatusColor(
                          suggestion.status
                        )}`}
                      >
                        {suggestion.status}
                      </span>
                      <span className="text-gray-500 text-sm">
                        Source: {suggestion.source} | Confidence: {suggestion.confidence_score.toFixed(2)}
                      </span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">{suggestion.issue_summary}</h3>
                    <div className="text-gray-600 mb-4">
                      <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-3 rounded">
                        {JSON.stringify(suggestion.suggested_action, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>

                {suggestion.status === SuggestionStatus.PENDING && (
                  <div className="flex space-x-2 mt-4">
                    <button
                      onClick={() => handleStatusUpdate(suggestion.id, SuggestionStatus.APPROVED)}
                      className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-md flex items-center text-sm"
                    >
                      <Check className="h-4 w-4 mr-1" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleStatusUpdate(suggestion.id, SuggestionStatus.SIMULATED)}
                      className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded-md flex items-center text-sm"
                    >
                      <Play className="h-4 w-4 mr-1" />
                      Simulate
                    </button>
                    <button
                      onClick={() => handleStatusUpdate(suggestion.id, SuggestionStatus.IGNORED)}
                      className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded-md flex items-center text-sm"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Ignore
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SuggestionsFeed;
