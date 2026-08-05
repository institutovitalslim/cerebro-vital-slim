'use client';

import { useRef, useState } from 'react';
import { api } from '@/lib/api';
import type { Hook } from '@/lib/types';
import styles from './HookCard.module.css';

interface HookCardProps {
  hook: Hook;
  selected?: boolean;
  onCompare?: (hook: Hook) => void;
  onAdapt?: (hook: Hook) => void;
}

const scoreLabels = {
  clarity: 'Clareza',
  specificity: 'Especificidade',
  novelty: 'Novidade',
  retention: 'Retenção',
  channel_fit: 'Aderência',
} as const;

async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement('textarea');
    area.value = text;
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.append(area);
    area.select();
    try {
      return document.execCommand('copy');
    } catch {
      return false;
    } finally {
      area.remove();
    }
  }
}

export function HookCard({ hook, selected = false, onCompare, onAdapt }: HookCardProps) {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const [favorite, setFavorite] = useState(Boolean(hook.favorite));
  const [favoriting, setFavoriting] = useState(false);
  const [favoriteError, setFavoriteError] = useState(false);
  const favoritingLock = useRef(false);
  const blocked = hook.compliance.status === 'block';

  async function favor() {
    if (favorite || favoritingLock.current) return;
    favoritingLock.current = true;
    setFavoriting(true);
    setFavoriteError(false);
    try {
      await api.favorite(hook.id);
      setFavorite(true);
    } catch {
      setFavoriteError(true);
    } finally {
      favoritingLock.current = false;
      setFavoriting(false);
    }
  }

  async function copy() {
    const succeeded = await copyText(hook.text);
    setCopied(succeeded);
    setCopyError(!succeeded);
  }

  const status = hook.compliance.status === 'pass'
    ? 'Aprovado na checagem'
    : hook.compliance.status === 'review' ? 'Requer revisão' : 'Bloqueado';

  return <article className={styles.card} aria-label={`Hook: ${hook.text}`}>
    <header>
      <span className={`${styles.status} ${styles[hook.compliance.status]}`}>{status}</span>
      <span className={styles.pattern}>{hook.pattern_id}</span>
    </header>
    <blockquote>{hook.text}</blockquote>
    <div className={styles.score}><strong>{Math.round(hook.scores.overall)}</strong><span>Score geral</span></div>
    <dl className={styles.dimensions}>
      {Object.entries(scoreLabels).map(([key, label]) => <div key={key}>
        <dt>{label}</dt><dd>{Math.round(hook.scores[key as keyof typeof scoreLabels])}</dd>
      </div>)}
    </dl>
    <p className={styles.explain}><b>{hook.mechanisms.join(', ')}</b> · {hook.explanation}</p>
    {hook.compliance.reasons.length > 0 && <p className={styles.reasons}>Motivos: {hook.compliance.reasons.join('; ')}</p>}
    <footer>
      <button type="button" onClick={copy}>{copied ? 'Copiado' : 'Copiar'}</button>
      <button type="button" onClick={favor} disabled={favorite || favoriting} aria-pressed={favorite}>{favorite ? 'Favoritado' : favoriting ? 'Favoritando…' : 'Favoritar'}</button>
      {onAdapt && <button type="button" onClick={() => onAdapt(hook)}>Adaptar</button>}
      {onCompare && <button
        type="button"
        disabled={blocked}
        aria-pressed={selected}
        title={blocked ? 'Hooks bloqueados não podem ser comparados' : undefined}
        onClick={() => onCompare(hook)}
      >
        {selected ? 'Remover da comparação' : 'Comparar'}
      </button>}
    </footer>
    {copyError && <small role="alert">Não foi possível copiar.</small>}
    {favoriteError && <small role="alert">Não foi possível favoritar.</small>}
  </article>;
}
