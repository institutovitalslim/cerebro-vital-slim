import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, test, vi } from 'vitest';
import Home from '@/app/page';
import Library from '@/app/library/page';
import { GeneratorForm } from '@/components/GeneratorForm';
import { HookCard } from '@/components/HookCard';
import { api } from '@/lib/api';
import type { GenerationResponse, Hook } from '@/lib/types';

const sampleHook: Hook = {
  id: '22222222-2222-4222-8222-222222222222',
  text: 'Um novo olhar para sono',
  language: 'pt-BR',
  library: 'universal',
  pattern_id: 'universal-test',
  mechanisms: ['curiosity_gap'],
  objective: 'retention',
  channel: 'reel',
  awareness_stage: 'problem_aware',
  audience: 'mulheres 40+',
  topic: 'sono',
  tone: 'premium',
  scores: { clarity: 90, specificity: 80, novelty: 75, retention: 88, channel_fit: 92, overall: 86 },
  compliance: { status: 'pass', reasons: [] },
  explanation: 'Abre uma lacuna.',
  source: 'deterministic',
  engine_version: '0.1.0',
  created_at: '2026-01-01T00:00:00Z',
};

const generation = (warnings: string[] = []): GenerationResponse => ({
  request_id: '11111111-1111-4111-8111-111111111111',
  hooks: [sampleHook],
  warnings,
  engine_version: '0.1.0',
  duration_ms: 2,
});

const response = (data: unknown): Response => ({
  ok: true,
  json: async () => data,
} as Response);

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('contratos do formulário', () => {
  test('oferece todos os canais e objetivos do backend', () => {
    render(<GeneratorForm onResult={vi.fn()} />);
    const values = (label: string) => Array.from(
      (screen.getByLabelText(label) as HTMLSelectElement).options,
      option => option.value,
    );

    expect(values('Canal')).toEqual([
      'reel', 'ad', 'carousel', 'story', 'landing_page', 'email', 'blog', 'youtube',
    ]);
    expect(values('Objetivo')).toEqual([
      'scroll_stop', 'curiosity', 'retention', 'identification', 'education',
      'authority', 'objection', 'sharing', 'action',
    ]);
  });

  test('aborta a geração anterior e ignora resposta stale sem mostrar AbortError', async () => {
    let firstSignal: AbortSignal | undefined;
    let resolveFirst!: (value: Response) => void;
    const first = new Promise<Response>(resolve => { resolveFirst = resolve; });
    const fetchMock = vi.fn()
      .mockImplementationOnce((_url: string, init?: RequestInit) => {
        firstSignal = init?.signal ?? undefined;
        return first;
      })
      .mockResolvedValueOnce(response({ ...generation(), hooks: [{ ...sampleHook, text: 'Resposta nova' }] }));
    vi.stubGlobal('fetch', fetchMock);
    const onResult = vi.fn();
    const { container } = render(<GeneratorForm onResult={onResult} />);
    await userEvent.type(screen.getByLabelText('Tema'), 'sono');
    await userEvent.type(screen.getByLabelText('Público'), 'adultos');

    fireEvent.submit(container.querySelector('form')!);
    fireEvent.submit(container.querySelector('form')!);

    await waitFor(() => expect(onResult).toHaveBeenCalledTimes(1));
    expect(firstSignal?.aborted).toBe(true);
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    resolveFirst(response({ ...generation(), hooks: [{ ...sampleHook, text: 'Resposta velha' }] }));
    await Promise.resolve();
    expect(onResult).toHaveBeenLastCalledWith(expect.objectContaining({
      hooks: [expect.objectContaining({ text: 'Resposta nova' })],
    }));
  });

  test('request preserva AbortError e encaminha AbortSignal', async () => {
    const controller = new AbortController();
    const fetchMock = vi.fn((_url: string, init?: RequestInit) => new Promise<Response>((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('cancelada', 'AbortError')));
    }));
    vi.stubGlobal('fetch', fetchMock);
    const pending = api.generate({
      topic: 'sono', audience: 'adultos', library: 'universal', channel: 'reel',
      objective: 'retention', awareness_stage: 'problem_aware', tone: 'premium',
      intensity: 2, mechanism: null, context: null, required_words: [], forbidden_words: [],
      count: 1, max_length: 180, use_ai: false,
    }, controller.signal);
    controller.abort();
    await expect(pending).rejects.toMatchObject({ name: 'AbortError' });
    expect(fetchMock.mock.calls[0][1]?.signal).toBe(controller.signal);
  });
});

describe('adaptação e mensagens públicas', () => {
  test('card só mostra Adaptar com callback e home preenche e foca Tema', async () => {
    const { rerender } = render(<HookCard hook={sampleHook} />);
    expect(screen.queryByRole('button', { name: 'Adaptar' })).not.toBeInTheDocument();
    const onAdapt = vi.fn();
    rerender(<HookCard hook={sampleHook} onAdapt={onAdapt} />);
    await userEvent.click(screen.getByRole('button', { name: 'Adaptar' }));
    expect(onAdapt).toHaveBeenCalledWith(sampleHook);

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response(generation())));
    cleanup();
    render(<Home />);
    await userEvent.type(screen.getByLabelText('Tema'), 'inicial');
    await userEvent.type(screen.getByLabelText('Público'), 'adultos');
    await userEvent.click(screen.getByRole('button', { name: 'Gerar hooks' }));
    await userEvent.click(await screen.findByRole('button', { name: 'Adaptar' }));
    expect(screen.getByLabelText('Tema')).toHaveValue('sono');
    expect(screen.getByLabelText('Tema')).toHaveFocus();
    expect(screen.getByLabelText('Contexto')).toHaveValue(
      `Adaptar com base neste rascunho: ${sampleHook.text}`,
    );
  });

  test('traduz warning conhecido e não reflete warning interno desconhecido', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response(generation([
      'AI unavailable; deterministic fallback used.',
      'token secreto do provedor interno',
    ]))));
    render(<Home />);
    await userEvent.type(screen.getByLabelText('Tema'), 'sono');
    await userEvent.type(screen.getByLabelText('Público'), 'adultos');
    await userEvent.click(screen.getByRole('button', { name: 'Gerar hooks' }));

    expect(await screen.findByText(
      'A adaptação por IA não ficou disponível; usamos a geração determinística.',
    )).toBeVisible();
    expect(screen.getByText('Um aviso interno foi ocultado. Tente novamente se necessário.')).toBeVisible();
    expect(screen.queryByText(/token secreto/)).not.toBeInTheDocument();
  });
});

describe('concorrência dos componentes', () => {
  test('favoritar bloqueia clique duplo enquanto a chamada está pendente', async () => {
    let finish!: (value: Response) => void;
    vi.stubGlobal('fetch', vi.fn(() => new Promise<Response>(resolve => { finish = resolve; })));
    render(<HookCard hook={sampleHook} />);
    const button = screen.getByRole('button', { name: 'Favoritar' });
    await userEvent.dblClick(button);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(button).toBeDisabled();
    finish(response({ id: sampleHook.id, favorite: true }));
    expect(await screen.findByRole('button', { name: 'Favoritado' })).toBeDisabled();
  });

  test('biblioteca aborta as duas consultas no unmount', () => {
    const signals: AbortSignal[] = [];
    vi.stubGlobal('fetch', vi.fn((_url: string, init?: RequestInit) => {
      if (init?.signal) signals.push(init.signal);
      return new Promise<Response>(() => undefined);
    }));
    const { unmount } = render(<Library />);
    unmount();
    expect(signals).toHaveLength(2);
    expect(signals.every(signal => signal.aborted)).toBe(true);
  });
});
