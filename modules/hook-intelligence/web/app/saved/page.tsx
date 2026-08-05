'use client';

import { useEffect, useRef, useState } from 'react';
import type { KeyboardEvent } from 'react';
import { HookCard } from '@/components/HookCard';
import { api, isAbortError } from '@/lib/api';
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
  const [retry, setRetry] = useState(0);
  const requestSequence = useRef(0);
  const activeRequest = useRef<{
    id: number;
    controller: AbortController;
  } | null>(null);
  const activeExport = useRef<{
    id: string;
    controller: AbortController;
  } | null>(null);

  function cancelActiveRequest() {
    const request = activeRequest.current;
    activeRequest.current = null;
    request?.controller.abort();
  }

  useEffect(() => {
    const controller = new AbortController();
    const requestId = ++requestSequence.current;
    cancelActiveRequest();
    activeRequest.current = { id: requestId, controller };
    const call = tab === 'history'
      ? api.history(page, controller.signal)
      : api.favorites(page, controller.signal);

    void call
      .then((data) => {
        if (controller.signal.aborted || activeRequest.current?.id !== requestId) return;
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
      .catch((caught) => {
        if (
          !controller.signal.aborted
          && activeRequest.current?.id === requestId
          && !isAbortError(caught)
        ) {
          setError(true);
        }
      })
      .finally(() => {
        if (activeRequest.current?.id === requestId) {
          activeRequest.current = null;
          setLoading(false);
        }
      });

    return () => {
      if (activeRequest.current?.id === requestId) activeRequest.current = null;
      controller.abort();
    };
  }, [page, retry, tab]);

  useEffect(() => () => {
    activeExport.current?.controller.abort();
    activeExport.current = null;
  }, []);

  const load = () => {
    cancelActiveRequest();
    setLoading(true);
    setError(false);
    setRetry((value) => value + 1);
  };

  function choose(value: SavedTab) {
    if (value === tab) return;
    cancelActiveRequest();
    setLoading(true);
    setError(false);
    setTab(value);
    setPage(1);
  }

  function navigateTabs(event: KeyboardEvent<HTMLButtonElement>) {
    let nextTab: SavedTab;
    if (event.key === 'Home') {
      nextTab = 'history';
    } else if (event.key === 'End') {
      nextTab = 'favorites';
    } else if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      nextTab = tab === 'history' ? 'favorites' : 'history';
    } else {
      return;
    }
    event.preventDefault();
    choose(nextTab);
    document.getElementById(`${nextTab}-tab`)?.focus();
  }

  async function download(id: string) {
    if (activeExport.current) return;
    const controller = new AbortController();
    activeExport.current = { id, controller };
    setExporting(id);
    try {
      const data = await api.exportSession(id, workspace.trim(), controller.signal);
      if (controller.signal.aborted || activeExport.current?.controller !== controller) return;
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
      document.body.appendChild(anchor);
      try {
        anchor.click();
      } finally {
        anchor.remove();
        URL.revokeObjectURL(url);
      }
    } catch (caught) {
      if (
        !controller.signal.aborted
        && activeExport.current?.controller === controller
        && !isAbortError(caught)
      ) {
        setError(true);
      }
    } finally {
      if (activeExport.current?.controller === controller) {
        activeExport.current = null;
        setExporting('');
      }
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
                        !workspace.trim() || Boolean(exporting)
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
          onClick={() => {
            cancelActiveRequest();
            setLoading(true);
            setPage((value) => value - 1);
          }}
        >
          <span aria-hidden="true">←</span> Anterior
        </button>
        <span aria-live="polite">
          Página <b>{page}</b>
        </span>
        <button
          type="button"
          disabled={page * PAGE_SIZE >= total || loading}
          onClick={() => {
            cancelActiveRequest();
            setLoading(true);
            setPage((value) => value + 1);
          }}
        >
          Próxima <span aria-hidden="true">→</span>
        </button>
      </nav>
    </main>
  );
}
