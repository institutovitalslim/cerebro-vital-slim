'use client';

import { useMemo, useRef, useState } from 'react';
import { GeneratorForm, type GeneratorFormHandle } from './_components/GeneratorForm';
import { HookCard } from './_components/HookCard';
import { ComparisonTray } from './_components/ComparisonTray';
import type { GenerationResponse, Hook } from './_lib/types';
import styles from './page.module.css';

const publicWarning = (warning: string) => warning === 'AI unavailable; deterministic fallback used.'
  ? 'A adaptação por IA não ficou disponível; usamos a geração determinística.'
  : 'Um aviso interno foi ocultado. Tente novamente se necessário.';

export default function Home() {
  const [result, setResult] = useState<GenerationResponse | null>(null);
  const [compare, setCompare] = useState<Hook[]>([]);
  const generatorRef = useRef<GeneratorFormHandle>(null);
  const warnings = useMemo(() => result?.warnings.map(publicWarning) ?? [], [result]);

  function toggle(hook: Hook) {
    setCompare(current => current.some(item => item.id === hook.id)
      ? current.filter(item => item.id !== hook.id)
      : current.length < 3 ? [...current, hook] : current);
  }

  function adapt(hook: Hook) {
    generatorRef.current?.adapt(hook);
  }

  return <main className={styles.workspace}>
    <GeneratorForm ref={generatorRef} onResult={setResult} />
    <section className={styles.results} aria-live="polite">
      <header>
        <div><span>02 / Seleção</span><h1>Hooks em análise</h1></div>
        {result && <small>{result.hooks.length} alternativas · motor {result.engine_version}</small>}
      </header>
      {!result
        ? <div className={styles.empty}><span>✦</span><h2>Seu painel está pronto</h2><p>Defina o briefing ao lado para criar alternativas avaliadas por clareza, retenção e conformidade.</p></div>
        : <>
          {warnings.map((warning, index) => <p className={styles.warning} key={`${index}-${warning}`}>{warning}</p>)}
          <div className={styles.grid}>{result.hooks.map(hook => <HookCard
            key={hook.id}
            hook={hook}
            selected={compare.some(item => item.id === hook.id)}
            onCompare={toggle}
            onAdapt={adapt}
          />)}</div>
        </>}
    </section>
    <ComparisonTray
      hooks={compare}
      onRemove={id => setCompare(current => current.filter(hook => hook.id !== id))}
      onClear={() => setCompare([])}
    />
  </main>;
}
