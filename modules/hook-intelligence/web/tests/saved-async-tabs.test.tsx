import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, test, vi } from 'vitest';
import Saved from '@/app/saved/page';
import { api } from '@/lib/api';
import type { HistoryItem, Hook, Page } from '@/lib/types';

const historyItem: HistoryItem = {
  request_id: '11111111-1111-4111-8111-111111111111',
  created_at: '2026-01-01T00:00:00Z',
  hook_count: 1,
};

const hook: Hook = {
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

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((ok, fail) => {
    resolve = ok;
    reject = fail;
  });
  return { promise, resolve, reject };
}

const page = <T,>(items: T[], total = items.length): Page<T> => ({
  items,
  total,
  page: 1,
  page_size: 20,
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe('concorrência da página de salvos', () => {
  test('aborta consulta anterior, ignora resposta stale e preserva loading da atual', async () => {
    const oldHistory = deferred<Page<HistoryItem>>();
    const currentFavorites = deferred<Page<Hook>>();
    let historySignal: AbortSignal | undefined;
    let favoritesSignal: AbortSignal | undefined;
    vi.spyOn(api, 'history').mockImplementation((_page, signal) => {
      historySignal = signal;
      return oldHistory.promise;
    });
    vi.spyOn(api, 'favorites').mockImplementation((_page, signal) => {
      favoritesSignal = signal;
      return currentFavorites.promise;
    });

    render(<Saved />);
    await userEvent.click(screen.getByRole('tab', { name: 'Favoritos' }));

    expect(historySignal?.aborted).toBe(true);
    expect(favoritesSignal?.aborted).toBe(false);
    oldHistory.resolve(page([historyItem], 99));
    await Promise.resolve();
    await Promise.resolve();
    expect(screen.getByRole('status')).toHaveTextContent('Carregando itens salvos');

    currentFavorites.resolve(page([hook], 1));
    expect(await screen.findByText(hook.text)).toBeVisible();
    expect(screen.getByText('1 itens salvos no arquivo.')).toBeVisible();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  test('aborta a consulta ativa no unmount sem publicar AbortError', () => {
    let signal: AbortSignal | undefined;
    vi.spyOn(api, 'history').mockImplementation((_page, currentSignal) => {
      signal = currentSignal;
      return new Promise((_resolve, reject) => {
        currentSignal?.addEventListener('abort', () => reject(new DOMException('cancelada', 'AbortError')));
      });
    });

    const { unmount } = render(<Saved />);
    unmount();
    expect(signal?.aborted).toBe(true);
  });

  test('bloqueia exportação duplicada e aborta export pendente no unmount', async () => {
    vi.spyOn(api, 'history').mockResolvedValue(page([historyItem]));
    let exportSignal: AbortSignal | undefined;
    const pendingExport = deferred<Awaited<ReturnType<typeof api.exportSession>>>();
    const exportSpy = vi.spyOn(api, 'exportSession').mockImplementation((_id, _workspace, signal) => {
      exportSignal = signal;
      return pendingExport.promise;
    });

    const { unmount } = render(<Saved />);
    await screen.findByText(historyItem.request_id);
    await userEvent.type(screen.getByLabelText(/Referência do workspace/), 'campanha-sono');
    const button = screen.getByRole('button', { name: 'Baixar JSON' });
    fireEvent.click(button);
    fireEvent.click(button);

    expect(exportSpy).toHaveBeenCalledTimes(1);
    expect(button).toBeDisabled();
    expect(exportSignal?.aborted).toBe(false);
    unmount();
    expect(exportSignal?.aborted).toBe(true);
  });
});

describe('navegação WAI-ARIA das abas', () => {
  test('setas, Home e End movem seleção, tabindex e foco deterministicamente', async () => {
    vi.spyOn(api, 'history').mockResolvedValue(page([]));
    vi.spyOn(api, 'favorites').mockResolvedValue(page([]));
    render(<Saved />);
    await screen.findByText('Nenhuma sessão gerada ainda.');
    const history = screen.getByRole('tab', { name: 'Histórico' });
    const favorites = screen.getByRole('tab', { name: 'Favoritos' });

    history.focus();
    fireEvent.keyDown(history, { key: 'ArrowLeft' });
    await waitFor(() => expect(favorites).toHaveFocus());
    expect(favorites).toHaveAttribute('aria-selected', 'true');
    expect(favorites).toHaveAttribute('tabindex', '0');
    expect(history).toHaveAttribute('tabindex', '-1');

    fireEvent.keyDown(favorites, { key: 'ArrowRight' });
    await waitFor(() => expect(history).toHaveFocus());
    fireEvent.keyDown(history, { key: 'End' });
    await waitFor(() => expect(favorites).toHaveFocus());
    fireEvent.keyDown(favorites, { key: 'Home' });
    await waitFor(() => expect(history).toHaveFocus());
    expect(history).toHaveAttribute('aria-selected', 'true');
  });
});
