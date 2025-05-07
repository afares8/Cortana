export interface PEPScreeningMatch {
  name: string;
  position: string;
  country: string;
  similarity_score: number;
}

export interface SanctionsScreeningMatch {
  name: string;
  list_source: string;
  country?: string;
  similarity_score: number;
}

export interface PEPScreeningResult {
  id: number;
  client_id: number;
  full_name: string;
  matches: PEPScreeningMatch[];
  created_at: string;
}

export interface SanctionsScreeningResult {
  id: number;
  client_id: number;
  entity_name: string;
  entity_type: string;
  matches: SanctionsScreeningMatch[];
  created_at: string;
}
