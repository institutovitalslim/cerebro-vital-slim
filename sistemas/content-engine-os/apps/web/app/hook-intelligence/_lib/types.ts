export type ComplianceStatus = 'pass' | 'review' | 'block';
export type Channel =
  | 'reel'
  | 'ad'
  | 'carousel'
  | 'story'
  | 'landing_page'
  | 'email'
  | 'blog'
  | 'youtube';
export type Objective =
  | 'scroll_stop'
  | 'curiosity'
  | 'retention'
  | 'identification'
  | 'education'
  | 'authority'
  | 'objection'
  | 'sharing'
  | 'action';
export type Library = 'universal' | 'ivs-health';
export type AwarenessStage =
  | 'unaware'
  | 'problem_aware'
  | 'solution_aware'
  | 'product_aware'
  | 'ready_to_act';
export type Tone = 'premium' | 'educational' | 'direct' | 'empathetic' | 'provocative';
export type Source = 'deterministic' | 'ai_adapted' | 'curated';

export interface Scores {
  clarity: number;
  specificity: number;
  novelty: number;
  retention: number;
  channel_fit: number;
  overall: number;
}

export interface Hook {
  id: string;
  text: string;
  language: 'pt-BR';
  library: Library;
  pattern_id: string;
  mechanisms: string[];
  objective: Objective;
  channel: Channel;
  awareness_stage: AwarenessStage;
  audience: string;
  topic: string;
  tone: Tone;
  scores: Scores;
  compliance: { status: ComplianceStatus; reasons: string[] };
  explanation: string;
  source: Source;
  engine_version: string;
  created_at: string;
  favorite?: boolean;
}

export interface ExportHook extends Hook {
  favorite: boolean;
}

export interface GenerationPayload {
  topic: string;
  audience: string;
  library: Library;
  channel: Channel;
  objective: Objective;
  awareness_stage: AwarenessStage;
  tone: Tone;
  intensity: number;
  mechanism: string | null;
  context: string | null;
  required_words: string[];
  forbidden_words: string[];
  count: number;
  max_length: number;
  use_ai: boolean;
}

export interface GenerationResponse {
  request_id: string;
  hooks: Hook[];
  warnings: string[];
  engine_version: string;
  duration_ms: number;
}

export interface Pattern {
  id: string;
  library: Library;
  mechanism: string;
  objectives: Objective[];
  channels: Channel[];
  awareness_stages: AwarenessStage[];
  tones: Tone[];
  template: string;
  slots: string[];
  explanation: string;
  intensity: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface HistoryItem {
  request_id: string;
  created_at: string;
  hook_count: number;
}

export interface ExportResponse {
  schema_version: '1.0.0';
  workspace_ref: string;
  generated_at: string;
  hooks: ExportHook[];
}
