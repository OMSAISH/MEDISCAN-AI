export type UserRole = "RESEARCHER" | "ADMIN";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  organization?: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface DrugValidation {
  is_valid: boolean;
  input_name: string;
  normalized_name: string;
  synonyms: string[];
  chembl_id?: string;
  pubchem_cid?: string;
  canonical_smiles?: string;
  known_indications: string[];
  warnings: string[];
}

export type QueryStatus = "QUEUED" | "RUNNING" | "COMPLETED" | "PARTIAL_FAILURE" | "FAILED";
export type AgentStatus = "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";
export type EvidenceStrength = "Strong" | "Moderate" | "Limited" | "Insufficient";
export type SourceType = "CLINICAL" | "LITERATURE" | "PATENT" | "MARKET";

export interface AgentRun {
  agent_name: string;
  status: AgentStatus;
  items_found: number;
  execution_time_ms?: number;
  error_message?: string;
  details?: Record<string, any>;
}

export interface Indication {
  id: string;
  indication_name: string;
  therapeutic_area?: string;
  evidence_score: number;
  clinical_score: number;
  literature_score: number;
  patent_score: number;
  market_score: number;
  evidence_strength: EvidenceStrength;
  clinical_trial_count: number;
  literature_count: number;
  patent_count: number;
  market_signal_count: number;
  phase_distribution?: Record<string, number>;
  positive_factors?: string[];
  limitations?: string[];
  explanation?: string;
}

export interface ResearchSummary {
  id: string;
  drug_name: string;
  normalized_drug_name: string;
  research_question?: string;
  status: QueryStatus;
  indication_count: number;
  clinical_trial_count: number;
  literature_count: number;
  patent_count: number;
  market_signal_count: number;
  created_at: string;
  execution_time_ms?: number;
}

export interface ResearchDetail {
  id: string;
  drug_name: string;
  normalized_drug_name: string;
  canonical_smiles?: string;
  chembl_id?: string;
  pubchem_cid?: string;
  research_question?: string;
  status: QueryStatus;
  error_message?: string;
  execution_time_ms?: number;
  executive_summary?: string;
  synthesis_disclaimer?: string;
  created_at: string;
  agent_runs: AgentRun[];
  indications: Indication[];
}

export interface EvidenceItem {
  id: string;
  query_id: string;
  indication_id?: string;
  source_type: SourceType;
  source_id: string;
  source_url: string;
  title: string;
  publication_date?: string;
  evidence_type: string;
  evidence_strength: string;
  extracted_facts?: Record<string, any>;
  provenance?: Record<string, any>;
  confidence: number;
}

export interface IndicationEvidenceList {
  indication_id: string;
  indication_name: string;
  evidence_score: number;
  evidence_strength: string;
  clinical_trials: EvidenceItem[];
  literature: EvidenceItem[];
  patents: EvidenceItem[];
  market_signals: EvidenceItem[];
}

export type ReportFormat = "PDF" | "HTML" | "JSON" | "CSV";

export interface Report {
  id: string;
  query_id: string;
  title: string;
  report_format: ReportFormat;
  file_path: string;
  file_size_bytes: number;
  generated_at: string;
  metadata_json?: Record<string, any>;
}

export interface SystemHealth {
  status: string;
  database_connected: boolean;
  version: string;
  uptime_seconds: number;
  active_analyses: number;
}

export interface AgentMetric {
  agent_name: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  avg_execution_time_ms: number;
}

export interface AdminOverview {
  system_health: SystemHealth;
  total_users: number;
  total_analyses: number;
  completed_analyses: number;
  failed_analyses: number;
  total_evidence_items: number;
  total_indications_discovered: number;
  agent_metrics: AgentMetric[];
  api_integrations_status: Record<string, { name: string; status: string; auth_required: boolean }>;
}

export interface AuditLogItem {
  id: string;
  user_id?: string;
  user_email?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  ip_address?: string;
  details?: Record<string, any>;
  created_at: string;
}
