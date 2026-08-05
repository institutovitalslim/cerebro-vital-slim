'use client';

import { useEffect, useMemo, useState } from 'react';
import { api, isAbortError } from '@/lib/api';
import type { Library as LibraryName, Pattern } from '@/lib/types';
import styles from './page.module.css';

export default function Library() {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [mechanisms, setMechanisms] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [library, setLibrary] = useState<LibraryName | ''>('');
  const [mechanism, setMechanism] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let stale = false;

    Promise.all([
      api.patterns(undefined, controller.signal),
      api.taxonomies(controller.signal),
    ]).then(([patternResponse, taxonomyResponse]) => {
      if (stale) return;
      setPatterns(patternResponse.items);
      setMechanisms(taxonomyResponse.mechanisms);
    }).catch(caught => {
      if (!stale && !isAbortError(caught)) setError(true);
    }).finally(() => {
      if (!stale) setLoading(false);
    });

    return () => {
      stale = true;
      controller.abort();
    };
  }, [retry]);

  const shown = useMemo(() => patterns.filter(pattern =>
    (!library || pattern.library === library)
    && (!mechanism || pattern.mechanism === mechanism)
    && `${pattern.template} ${pattern.explanation}`
      .toLocaleLowerCase('pt-BR')
      .includes(search.toLocaleLowerCase('pt-BR')),
  ), [patterns, search, library, mechanism]);

  function load() {
    setLoading(true);
    setError(false);
    setRetry(value => value + 1);
  }

  return <main className={styles.page}>
    <header><span>CATÁLOGO EDITORIAL</span><h1>Biblioteca de padrões</h1><p>Estruturas reais do motor, prontas para consulta e direção criativa.</p></header>
    <div className={styles.filters}>
      <label>Buscar padrões<input value={search} onChange={event => setSearch(event.target.value)} type="search" /></label>
      <label>Biblioteca<select value={library} onChange={event => setLibrary(event.target.value as LibraryName | '')}><option value="">Todas</option><option value="universal">Universal</option><option value="ivs-health">IVS Health</option></select></label>
      <label>Mecanismo<select value={mechanism} onChange={event => setMechanism(event.target.value)}><option value="">Todos</option>{mechanisms.map(item => <option key={item}>{item}</option>)}</select></label>
    </div>
    {loading
      ? <p role="status">Carregando biblioteca…</p>
      : error
        ? <div role="alert" className={styles.error}>A biblioteca não pôde ser carregada. <button onClick={load}>Tentar novamente</button></div>
        : shown.length === 0
          ? <p>Nenhum padrão corresponde aos filtros.</p>
          : <div className={styles.catalog}>{shown.map(pattern => <article key={pattern.id}>
            <header><span>{pattern.library}</span><strong>{pattern.mechanism}</strong></header>
            <h2>{pattern.template}</h2><p>{pattern.explanation}</p>
            <dl><div><dt>Objetivos</dt><dd>{pattern.objectives.join(', ')}</dd></div><div><dt>Canais</dt><dd>{pattern.channels.join(', ')}</dd></div><div><dt>Intensidade</dt><dd>{pattern.intensity}</dd></div></dl>
          </article>)}</div>}
  </main>;
}
