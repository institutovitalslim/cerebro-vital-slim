import type {
  ExportResponse,
  GenerationPayload,
  GenerationResponse,
  HistoryItem,
  Hook,
  Library,
  Page,
  Pattern,
} from './types';

const BASE = '/api/hook-intelligence';

export class PublicApiError extends Error {
  constructor() {
    super('Não foi possível concluir. Verifique a conexão e tente novamente.');
    this.name = 'PublicApiError';
  }
}

export const isAbortError = (error: unknown): boolean =>
  typeof error === 'object'
  && error !== null
  && 'name' in error
  && error.name === 'AbortError';

export async function request<T>(
  path: string,
  init: RequestInit = {},
  signal?: AbortSignal,
): Promise<T> {
  try {
    const response = await fetch(`${BASE}${path}`, {
      ...init,
      signal: signal ?? init.signal,
      headers: { 'Content-Type': 'application/json', ...init.headers },
    });
    if (!response.ok) throw new PublicApiError();
    return await response.json() as T;
  } catch (error) {
    if (error instanceof PublicApiError || isAbortError(error)) {
      throw error;
    }
    throw new PublicApiError();
  }
}

export const api = {
  generate: (payload: GenerationPayload, signal?: AbortSignal) =>
    request<GenerationResponse>('/v1/hooks/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }, signal),
  favorite: (id: string, signal?: AbortSignal) =>
    request<{ id: string; favorite: true }>(
      `/v1/hooks/${encodeURIComponent(id)}/favorite`,
      { method: 'POST' },
      signal,
    ),
  patterns: (library?: Library, signal?: AbortSignal) =>
    request<{ items: Pattern[]; total: number }>(
      `/v1/patterns${library ? `?library=${encodeURIComponent(library)}` : ''}`,
      {},
      signal,
    ),
  taxonomies: (signal?: AbortSignal) =>
    request<{ taxonomies: Record<string, string[]>; mechanisms: string[] }>(
      '/v1/taxonomies',
      {},
      signal,
    ),
  history: (page = 1, signal?: AbortSignal) =>
    request<Page<HistoryItem>>(`/v1/history?page=${page}&page_size=20`, {}, signal),
  favorites: (page = 1, signal?: AbortSignal) =>
    request<Page<Hook>>(`/v1/favorites?page=${page}&page_size=20`, {}, signal),
  exportSession: (session_id: string, workspace_ref: string, signal?: AbortSignal) =>
    request<ExportResponse>('/v1/exports/content-os', {
      method: 'POST',
      body: JSON.stringify({ session_id, workspace_ref }),
    }, signal),
};
