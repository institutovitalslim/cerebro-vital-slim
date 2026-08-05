export type ComplianceStatus = 'pass' | 'review' | 'block';
export interface Scores { clarity:number; specificity:number; novelty:number; retention:number; channel_fit:number; overall:number }
export interface Hook { id:string; text:string; language:'pt-BR'; library:'universal'|'ivs-health'; pattern_id:string; mechanisms:string[]; objective:string; channel:string; awareness_stage:string; audience:string; topic:string; tone:string; scores:Scores; compliance:{status:ComplianceStatus; reasons:string[]}; explanation:string; source:string; engine_version:string; created_at:string; favorite?:boolean }
export interface GenerationPayload { topic:string; audience:string; library:'universal'|'ivs-health'; channel:string; objective:string; awareness_stage:string; tone:string; intensity:number; mechanism:string|null; context:string|null; required_words:string[]; forbidden_words:string[]; count:number; max_length:number; use_ai:boolean }
export interface GenerationResponse { request_id:string; hooks:Hook[]; warnings:string[]; engine_version:string; duration_ms:number }
export interface Pattern { id:string; library:'universal'|'ivs-health'; mechanism:string; objectives:string[]; channels:string[]; awareness_stages:string[]; tones:string[]; template:string; slots:string[]; explanation:string; intensity:number }
export interface Page<T> { items:T[]; total:number; page:number; page_size:number }
export interface HistoryItem { request_id:string; created_at:string; hook_count:number }
export interface ExportResponse { schema_version:'1.0.0'; workspace_ref:string; generated_at:string; hooks:Hook[] }
