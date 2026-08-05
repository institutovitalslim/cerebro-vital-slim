import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, vi, test, expect } from 'vitest';
import Home from '@/app/page';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

test('preenche briefing, gera hooks e apresenta score geral', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({
    request_id: '11111111-1111-4111-8111-111111111111', warnings: [], engine_version: '0.1.0', duration_ms: 2,
    hooks: [{ id: '22222222-2222-4222-8222-222222222222', text: 'Um novo olhar para sono', language: 'pt-BR', library: 'universal', pattern_id: 'universal-test', mechanisms: ['curiosity_gap'], objective: 'retention', channel: 'reel', awareness_stage: 'problem_aware', audience: 'mulheres 40+', topic: 'sono', tone: 'premium', scores: { clarity: 90, specificity: 80, novelty: 75, retention: 88, channel_fit: 92, overall: 86 }, compliance: { status: 'pass', reasons: [] }, explanation: 'Abre uma lacuna de curiosidade.', source: 'deterministic', engine_version: '0.1.0', created_at: '2026-01-01T00:00:00Z' }]
  }) }));
  render(<Home />);
  await userEvent.type(screen.getByLabelText('Tema'), 'sono');
  await userEvent.type(screen.getByLabelText('Público'), 'mulheres 40+');
  await userEvent.click(screen.getByRole('button', { name: 'Gerar hooks' }));
  expect(await screen.findByText('Score geral')).toBeInTheDocument();
  expect(screen.getByText('86')).toBeInTheDocument();
  const [, init] = vi.mocked(fetch).mock.calls[0];
  const payload = JSON.parse(String(init?.body)) as Record<string, unknown>;
  expect(payload).toMatchObject({ topic: 'sono', audience: 'mulheres 40+', count: 12, max_length: 180, use_ai: false, required_words: [], forbidden_words: [] });
});

test('mantém loading visível e permite tentar novamente após erro seguro', async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce({ ok: false, json: async () => ({ detail: 'segredo interno' }) }).mockResolvedValueOnce({ ok: true, json: async () => ({ request_id: '11111111-1111-4111-8111-111111111111', hooks: [], warnings: [], engine_version: '0.1.0', duration_ms: 1 }) });
  vi.stubGlobal('fetch', fetchMock);
  render(<Home />);
  await userEvent.type(screen.getByLabelText('Tema'), 'sono');
  await userEvent.type(screen.getByLabelText('Público'), 'adultos');
  await userEvent.click(screen.getByRole('button', { name: 'Gerar hooks' }));
  expect(await screen.findByRole('alert')).not.toHaveTextContent('segredo interno');
  await userEvent.click(screen.getByRole('button', { name: 'Gerar hooks' }));
  expect(await screen.findByText('0 alternativas · motor 0.1.0')).toBeVisible();
  expect(fetchMock).toHaveBeenCalledTimes(2);
});
