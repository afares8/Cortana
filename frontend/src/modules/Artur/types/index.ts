export interface ArturInsight {
  id: number;
  category: string;
  entity_type: string;
  entity_id?: number;
  department_id?: number;
  metrics: Record<string, unknown>;
  context: Record<string, unknown>;
  created_at: string;
}

export interface ArturSuggestion {
  id: number;
  department_id?: number;
  issue_summary: string;
  suggested_action: Record<string, unknown>;
  confidence_score: number;
  source: string;
  status: string;
  created_at: string;
  updated_at?: string;
}

export interface ArturIntervention {
  id: number;
  suggestion_id: number;
  intervention_type: string;
  department_id?: number;
  state_before: Record<string, unknown>;
  state_after: Record<string, unknown>;
  status: string;
  created_at: string;
  executed_at?: string;
  user_id?: number;
}

export interface ArturSimulation {
  id: number;
  suggestion_id: number;
  simulation_parameters: Record<string, unknown>;
  expected_outcomes: Record<string, unknown>;
  actual_outcomes: Record<string, unknown>;
  dependencies: Array<Record<string, unknown>>;
  status: string;
  result?: string;
  created_at: string;
  completed_at?: string;
}

export interface DepartmentHealth {
  department_id: number;
  department_name: string;
  health_score: number;
  active_suggestions: number;
  recent_interventions: number;
  metrics: Record<string, unknown>;
}

export const InsightCategory = {
  DEPARTMENT_CREATION: "department_creation",
  FUNCTION_USAGE: "function_usage",
  RULE_EXECUTION: "rule_execution",
  AI_CONSUMPTION: "ai_consumption",
  ORPHANED_ENTITY: "orphaned_entity",
  INACTIVE_ENTITY: "inactive_entity",
  OVERLAPPING_ENTITY: "overlapping_entity"
};

export const EntityType = {
  DEPARTMENT: "department",
  ROLE: "role",
  FUNCTION: "function",
  AUTOMATION_RULE: "automation_rule",
  USER: "user",
  AI_PROFILE: "ai_profile"
};

export const SuggestionStatus = {
  PENDING: "pending",
  APPROVED: "approved",
  EXECUTED: "executed",
  IGNORED: "ignored",
  SIMULATED: "simulated"
};

export const InterventionStatus = {
  PENDING: "pending",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  FAILED: "failed",
  ROLLED_BACK: "rolled_back"
};

export const SimulationStatus = {
  PENDING: "pending",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed"
};

export const SimulationResultType = {
  RECOMMENDED: "recommended",
  NEUTRAL: "neutral",
  NOT_RECOMMENDED: "not_recommended"
};

export interface HeatmapDataItem {
  department_id: number;
  department_name: string;
  ia_token_usage: number;
  function_executions: number;
  rule_triggers: number;
  health_score: number;
  hotspots: Array<{
    type: string;
    entity_id: number;
    value: number;
    coordinates: { x: number; y: number };
  }>;
}

export interface HeatmapData {
  items: HeatmapDataItem[];
  max_token_usage: number;
  max_executions: number;
  max_triggers: number;
}

export interface Prediction {
  id: number;
  department_id: number;
  department_name: string;
  prediction_type: string;
  summary: string;
  details: Record<string, unknown>;
  confidence: number;
  impact_score: number;
  predicted_timestamp: string;
}

export interface SimulationResult {
  id: number;
  suggestion_id: number;
  simulation_type: string;
  parameters: Record<string, unknown>;
  before_state: Record<string, unknown>;
  after_state: Record<string, unknown>;
  dependencies: Array<{
    entity_type: string;
    entity_id: number;
    impact_level: string;
    details: Record<string, unknown>;
  }>;
  result_type: string;
  confidence_score: number;
  created_at: string;
}
