'use client';

import { useCallback, useEffect, useState } from 'react';
import type { KeyboardEvent } from 'react';
import { HookCard } from '@/components/HookCard';
import { api } from '@/lib/api';
import type { HistoryItem, Hook } from '@/lib/types';
import styles from './page.module.css';

type SavedTab = 'history' | 'favorites';

const PAGE_SIZE = 20;
const safe = (value: string) =>
  value.replace(/[^a-zA-Z0-9_-]/g, '-').slice(0, 80) || 'workspace';

export default function Saved() {
  const [tab, setTab] = useState<SavedTab>('history');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [favorites, setFavorites] = useState<Hook[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [workspace, setWorkspace] = useState('');
  const [exporting, setExporting] = useState('');

  const fetchItems = useCallback(() => {
    const call = tab === 'history' ? api.history(page) : api.favorites(page);

    return call
      .then((data) => {
        setTotal(data.total);
        if (tab === 'history') {
          setHistory(data.items as HistoryItem[]);
        } else {
          setFavorites(
            (data.items as Hook[]).filter(
              (hook) => hook.compliance.status !== 'block',
            ),
          );
        }
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [page, tab]);

  const load = () => {
    setLoading(true);
    setError(false);
    void fetchItems();
  };

  useEffect(() => {
    void fetchItems();
  }, [fetchItems]);

  function choose(value: SavedTab) {
    setLoading(true);
    setError(false);
    setTab(value);
    setPage(1);
  }

  function navigateTabs(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const nextTab = tab === 'history' ? 'favorites' : 'history';
    choose(nextTab);
    document.getElementById(`${nextTab}-tab`)?.focus();
  }

  async function download(id: string) {
    setExporting(id);
    try {
      const data = await api.exportSession(id, workspace.trim());
      const clean = {
        ...data,
        hooks: data.hooks.filter(
          (hook) => hook.compliance.status !== 'block',
        ),
      };
      const blob = new Blob([JSON.stringify(clean, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `hooks-${safe(workspace)}-${id.slice(0, 8)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch {
      setError(true);
    } finally {
      setExporting('');
    }
  }

  const panelLabel = `${tab}-tab`;

  return (
    <main className={styles.page}>
      <header className={styles.hero}>
        <div>
          <span className={styles.eyebrow}>ARQUIVO EDITORIAL</span>
          <h1>Histórico &amp; favoritos</h1>
        </div>
        <p>Recupere sessões e baixe lotes validados sem publicar conteúdo.</p>
      </header>

      <div
        className={styles.tabs}
        role="tablist"
        aria-label="Itens salvos"
      >
        <button
          id="history-tab"
          type="button"
          role="tab"
          aria-controls="saved-panel"
          aria-selected={tab === 'history'}
          tabIndex={tab === 'history' ? 0 : -1}
          onClick={() => choose('history')}
          onKeyDown={navigateTabs}
        >
          Histórico
        </button>
        <button
          id="favorites-tab"
          type="button"
          role="tab"
          aria-controls="saved-panel"
          aria-selected={tab === 'favorites'}
          tabIndex={tab === 'favorites' ? 0 : -1}
          onClick={() => choose('favorites')}
          onKeyDown={navigateTabs}
        >
          Favoritos
        </button>
      </div>

      <section
        id="saved-panel"
        className={styles.panel}
        role="tabpanel"
        aria-labelledby={panelLabel}
        aria-busy={loading}
        tabIndex={0}
      >
        {loading ? (
          <div className={styles.status} role="status">
            <span className={styles.loader} aria-hidden="true" />
            <p>Carregando itens salvos…</p>
          </div>
        ) : error ? (
          <div role="alert" className={styles.error}>
            <div>
              <strong>O arquivo está temporariamente indisponível.</strong>
              <p>Não foi possível carregar ou exportar os itens salvos.</p>
            </div>
            <button type="button" onClick={load}>
              Tentar novamente
            </button>
          </div>
        ) : tab === 'history' ? (
          <div className={styles.historyView}>
            <div className={styles.workspaceRow}>
              <div className={styles.sectionIntro}>
                <span>SESSÕES DE GERAÇÃO</span>
                <h2>Workspace de exportação</h2>
                <p>
                  Identifique o projeto para preparar um arquivo JSON rastreável.
                </p>
              </div>
              <label className={styles.workspace}>
                Referência do workspace
                <input
                  required
                  maxLength={256}
                  value={workspace}
                  aria-describedby="workspace-help"
                  placeholder="Ex.: campanha-sono-agosto"
                  onChange={(event) =>
                    setWorkspace(event.target.value.replace(/[<>]/g, ''))
                  }
                />
                <small id="workspace-help">
                  Obrigatória para habilitar o download.
                </small>
              </label>
            </div>

            {history.length === 0 ? (
              <div className={styles.empty}>
                <span aria-hidden="true">◇</span>
                <h2>Nenhuma sessão gerada ainda.</h2>
                <p>As próximas gerações aparecerão aqui para exportação.</p>
              </div>
            ) : (
              <div className={styles.sessions}>
                {history.map((item) => (
                  <article key={item.request_id}>
                    <div className={styles.sessionMeta}>
                      <span>LOTE VALIDADO</span>
                      <b>{item.hook_count} hooks</b>
                      <time dateTime={item.created_at}>
                        {new Date(item.created_at).toLocaleString('pt-BR')}
                      </time>
                      <small>{item.request_id}</small>
                    </div>
                    <button
                      type="button"
                      disabled={
                        !workspace.trim() || exporting === item.request_id
                      }
                      aria-describedby="workspace-help"
                      onClick={() => download(item.request_id)}
                    >
                      {exporting === item.request_id
                        ? 'Preparando…'
                        : 'Baixar JSON'}
                    </button>
                  </article>
                ))}
              </div>
            )}
          </div>
        ) : favorites.length === 0 ? (
          <div className={styles.empty}>
            <span aria-hidden="true">♡</span>
            <h2>Nenhum favorito disponível.</h2>
            <p>Favorite hooks aprovados para montar sua seleção editorial.</p>
          </div>
        ) : (
          <div className={styles.favoriteView}>
            <div className={styles.sectionIntro}>
              <span>CURADORIA ATIVA</span>
              <h2>Seleção editorial</h2>
              <p>{total} itens salvos no arquivo.</p>
            </div>
            <div className={styles.cards}>
              {favorites.map((hook) => (
                <HookCard
                  key={hook.id}
                  hook={{ ...hook, favorite: true }}
                />
              ))}
            </div>
          </div>
        )}
      </section>

      <nav className={styles.pagination} aria-label="Paginação de itens salvos">
        <button
          type="button"
          disabled={page === 1 || loading}
          onClick={() => setPage((value) => value - 1)}
        >
          <span aria-hidden="true">←</span> Anterior
        </button>
        <span aria-live="polite">
          Página <b>{page}</b>
        </span>
        <button
          type="button"
          disabled={page * PAGE_SIZE >= total || loading}
          onClick={() => setPage((value) => value + 1)}
        >
          Próxima <span aria-hidden="true">→</span>
        </button>
      </nav>
    </main>
  );
}
