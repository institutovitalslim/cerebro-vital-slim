import type { ExportResponse, GenerationPayload, GenerationResponse, HistoryItem, Hook, Page, Pattern } from './types';
const BASE='/api/backend';
export class PublicApiError extends Error { constructor(){ super('Não foi possível concluir. Verifique a conexão e tente novamente.'); this.name='PublicApiError'; } }
async function request<T>(path:string, init?:RequestInit):Promise<T>{
  try { const response=await fetch(`${BASE}${path}`,{...init,headers:{'Content-Type':'application/json',...init?.headers}}); if(!response.ok) throw new PublicApiError(); return await response.json() as T; } catch(error){ if(error instanceof PublicApiError) throw error; throw new PublicApiError(); }
}
export const api={
 generate:(payload:GenerationPayload)=>request<GenerationResponse>('/v1/hooks/generate',{method:'POST',body:JSON.stringify(payload)}),
 favorite:(id:string)=>request<{id:string;favorite:true}>(`/v1/hooks/${encodeURIComponent(id)}/favorite`,{method:'POST'}),
 patterns:(library?:string)=>request<{items:Pattern[];total:number}>(`/v1/patterns${library?`?library=${encodeURIComponent(library)}`:''}`),
 taxonomies:()=>request<{taxonomies:Record<string,string[]>;mechanisms:string[]}>('/v1/taxonomies'),
 history:(page=1)=>request<Page<HistoryItem>>(`/v1/history?page=${page}&page_size=20`),
 favorites:(page=1)=>request<Page<Hook>>(`/v1/favorites?page=${page}&page_size=20`),
 exportSession:(session_id:string,workspace_ref:string)=>request<ExportResponse>('/v1/exports/content-os',{method:'POST',body:JSON.stringify({session_id,workspace_ref})}),
};
