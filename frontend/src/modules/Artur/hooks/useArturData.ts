import { useState, useEffect, useCallback } from 'react';
import {
  getInsights,
  getSuggestions,
  getInterventions,
  getInterventionLogs,
  getDepartmentHealth,
  getHeatmapData,
  getPredictions,
  simulateIntervention,
  executeIntervention,
  updateSuggestionStatus
} from '../api/arturApi';
import {
  ArturInsight,
  ArturSuggestion,
  ArturIntervention,
  DepartmentHealth,
  HeatmapData,
  Prediction,
  SimulationResult
} from '../types';

interface FetchState<T> {
  data: T;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useInsights = (
  params: {
    category?: string;
    entity_type?: string;
    department_id?: number;
  } = {}
): FetchState<ArturInsight[]> => {
  const [data, setData] = useState<ArturInsight[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getInsights(params);
      setData(result);
      setError(null);
    } catch (err) {
      setError('Failed to fetch insights');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

export const useSuggestions = (
  params: {
    status?: string;
    department_id?: number;
    source?: string;
    min_confidence?: number;
  } = {}
): FetchState<ArturSuggestion[]> => {
  const [data, setData] = useState<ArturSuggestion[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getSuggestions(params);
      setData(result);
      setError(null);
    } catch (err) {
      setError('Failed to fetch suggestions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

export const useInterventions = (
  params: {
    status?: string;
    intervention_type?: string;
    department_id?: number;
  } = {}
): FetchState<ArturIntervention[]> => {
  const [data, setData] = useState<ArturIntervention[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getInterventions(params);
      setData(result);
      setError(null);
    } catch (err) {
      setError('Failed to fetch interventions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

export const useInterventionLogs = (
  params: {
    department_id?: number;
    from_date?: string;
    to_date?: string;
    action_type?: string;
  } = {},
  autoRefresh: boolean = true
): FetchState<ArturIntervention[]> => {
  const [data, setData] = useState<ArturIntervention[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getInterventionLogs(params);
      setData(result);
      setError(null);
    } catch (err) {
      setError('Failed to fetch intervention logs');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchData();

    let intervalId: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      intervalId = setInterval(fetchData, 60000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [fetchData, autoRefresh]);

  return { data, loading, error, refetch: fetchData };
};

export const useDepartmentHealth = (): FetchState<DepartmentHealth[]> => {
  const [data, setData] = useState<DepartmentHealth[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getDepartmentHealth();
      setData(result);
      setError(null);
    } catch (err) {
      setError('Failed to fetch department health');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

export const useHeatmapData = (): FetchState<HeatmapData> => {
  const [data, setData] = useState<HeatmapData>({ 
    items: [], 
    max_token_usage: 0, 
    max_executions: 0, 
    max_triggers: 0 
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getHeatmapData();
      setData(result);
      setError(null);
    } catch (err) {
      setError('Failed to fetch heatmap data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

export const usePredictions = (
  autoRefresh: boolean = true
): FetchState<Prediction[]> => {
  const [data, setData] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getPredictions();
      setData(result);
      setError(null);
    } catch (err) {
      setError('Failed to fetch predictions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    let intervalId: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      intervalId = setInterval(fetchData, 300000); // 5 minutes in milliseconds
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [fetchData, autoRefresh]);

  return { data, loading, error, refetch: fetchData };
};

export const useSimulateIntervention = () => {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const runSimulation = async (
    params: {
      suggestion_id: number;
      simulation_type: string;
      parameters?: Record<string, unknown>;
    }
  ): Promise<SimulationResult | null> => {
    try {
      setLoading(true);
      const simulationResult = await simulateIntervention(params);
      setResult(simulationResult);
      setError(null);
      return simulationResult;
    } catch (err) {
      setError('Failed to run simulation');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { result, loading, error, runSimulation };
};

export const useExecuteIntervention = () => {
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async (
    intervention_id: number,
    user_id?: number
  ): Promise<boolean> => {
    try {
      setLoading(true);
      await executeIntervention(intervention_id, user_id);
      setSuccess(true);
      setError(null);
      return true;
    } catch (err) {
      setError('Failed to execute intervention');
      console.error(err);
      setSuccess(false);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { success, loading, error, execute };
};

export const useUpdateSuggestionStatus = () => {
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const update = async (
    id: number,
    status: string
  ): Promise<boolean> => {
    try {
      setLoading(true);
      await updateSuggestionStatus(id, status);
      setSuccess(true);
      setError(null);
      return true;
    } catch (err) {
      setError('Failed to update suggestion status');
      console.error(err);
      setSuccess(false);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { success, loading, error, update };
};
