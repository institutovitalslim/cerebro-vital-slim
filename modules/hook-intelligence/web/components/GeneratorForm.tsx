'use client';

import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';
import { api, isAbortError } from '@/lib/api';
import type {
  Channel,
  GenerationPayload,
  GenerationResponse,
  Hook,
  Objective,
} from '@/lib/types';
import styles from './GeneratorForm.module.css';

interface GeneratorFormProps {
  onResult: (value: GenerationResponse) => void;
}

export interface GeneratorFormHandle {
  adapt: (hook: Hook) => void;
}

const channels: Array<{ value: Channel; label: string }> = [
  { value: 'reel', label: 'Reel' },
  { value: 'ad', label: 'Anúncio' },
  { value: 'carousel', label: 'Carrossel' },
  { value: 'story', label: 'Story' },
  { value: 'landing_page', label: 'Landing page' },
  { value: 'email', label: 'E-mail' },
  { value: 'blog', label: 'Blog' },
  { value: 'youtube', label: 'YouTube' },
];

const objectives: Array<{ value: Objective; label: string }> = [
  { value: 'scroll_stop', label: 'Interromper rolagem' },
  { value: 'curiosity', label: 'Curiosidade' },
  { value: 'retention', label: 'Retenção' },
  { value: 'identification', label: 'Identificação' },
  { value: 'education', label: 'Educação' },
  { value: 'authority', label: 'Autoridade' },
  { value: 'objection', label: 'Superar objeção' },
  { value: 'sharing', label: 'Compartilhamento' },
  { value: 'action', label: 'Ação' },
];

const initial: GenerationPayload = {
  topic: '',
  audience: '',
  library: 'universal',
  channel: 'reel',
  objective: 'retention',
  awareness_stage: 'problem_aware',
  tone: 'premium',
  intensity: 2,
  mechanism: null,
  context: null,
  required_words: [],
  forbidden_words: [],
  count: 12,
  max_length: 180,
  use_ai: false,
};

const split = (value: string) => value.split(',').map(item => item.trim()).filter(Boolean);

export const GeneratorForm = forwardRef<GeneratorFormHandle, GeneratorFormProps>(function GeneratorForm(
  { onResult },
  ref,
) {
  const [form, setForm] = useState(initial);
  const [required, setRequired] = useState('');
  const [forbidden, setForbidden] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const topicRef = useRef<HTMLInputElement>(null);
  const activeRequest = useRef<{ controller: AbortController; id: number } | null>(null);
  const nextRequestId = useRef(0);

  useEffect(() => () => activeRequest.current?.controller.abort(), []);

  useImperativeHandle(ref, () => ({
    adapt(hook: Hook) {
      setForm(current => ({
        ...current,
        topic: hook.topic,
        context: `Adaptar com base neste rascunho: ${hook.text}`,
      }));
      topicRef.current?.focus();
    },
  }), []);

  const set = <K extends keyof GenerationPayload>(key: K, value: GenerationPayload[K]) => {
    setForm(current => ({ ...current, [key]: value }));
  };

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    activeRequest.current?.controller.abort();
    const request = { controller: new AbortController(), id: ++nextRequestId.current };
    activeRequest.current = request;
    setLoading(true);
    setError(false);

    try {
      const result = await api.generate({
        ...form,
        required_words: split(required),
        forbidden_words: split(forbidden),
      }, request.controller.signal);
      if (activeRequest.current?.id === request.id) onResult(result);
    } catch (caught) {
      if (activeRequest.current?.id === request.id && !isAbortError(caught)) {
        setError(true);
      }
    } finally {
      if (activeRequest.current?.id === request.id) {
        activeRequest.current = null;
        setLoading(false);
      }
    }
  }

  return <form className={styles.form} onSubmit={submit} aria-label="Briefing do gerador">
    <div className={styles.heading}><span>01 / Briefing</span><h2>Direção editorial</h2></div>
    <label>Tema<input ref={topicRef} id="topic" required minLength={2} value={form.topic} onChange={event => set('topic', event.target.value)} /></label>
    <label>Público<input required minLength={2} value={form.audience} onChange={event => set('audience', event.target.value)} /></label>
    <div className={styles.two}>
      <label>Biblioteca<select value={form.library} onChange={event => set('library', event.target.value as GenerationPayload['library'])}><option value="universal">Universal</option><option value="ivs-health">IVS Health</option></select></label>
      <label>Canal<select value={form.channel} onChange={event => set('channel', event.target.value as Channel)}>{channels.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
    </div>
    <div className={styles.two}>
      <label>Objetivo<select value={form.objective} onChange={event => set('objective', event.target.value as Objective)}>{objectives.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
      <label>Consciência<select value={form.awareness_stage} onChange={event => set('awareness_stage', event.target.value as GenerationPayload['awareness_stage'])}><option value="unaware">Inconsciente</option><option value="problem_aware">Ciente do problema</option><option value="solution_aware">Ciente da solução</option><option value="product_aware">Ciente do produto</option><option value="ready_to_act">Pronto para agir</option></select></label>
    </div>
    <div className={styles.two}>
      <label>Tom<select value={form.tone} onChange={event => set('tone', event.target.value as GenerationPayload['tone'])}><option value="premium">Premium</option><option value="educational">Educativo</option><option value="direct">Direto</option><option value="empathetic">Empático</option><option value="provocative">Provocativo</option></select></label>
      <label>Intensidade<select value={form.intensity} onChange={event => set('intensity', Number(event.target.value))}><option value="1">Sutil</option><option value="2">Equilibrada</option><option value="3">Alta</option></select></label>
    </div>
    <label>Mecanismo<input value={form.mechanism ?? ''} onChange={event => set('mechanism', event.target.value || null)} placeholder="Opcional: curiosity_gap" /></label>
    <label>Contexto<textarea value={form.context ?? ''} onChange={event => set('context', event.target.value || null)} rows={3} /></label>
    <div className={styles.two}><label>Palavras obrigatórias<input value={required} onChange={event => setRequired(event.target.value)} aria-describedby="words-help" /></label><label>Palavras proibidas<input value={forbidden} onChange={event => setForbidden(event.target.value)} /></label></div>
    <small id="words-help">Separe termos por vírgulas.</small>
    <div className={styles.three}><label>Quantidade<input type="number" min={1} max={50} value={form.count} onChange={event => set('count', Number(event.target.value))} /></label><label>Máx. caracteres<input type="number" min={30} max={280} value={form.max_length} onChange={event => set('max_length', Number(event.target.value))} /></label><label className={styles.check}><input type="checkbox" checked={form.use_ai} onChange={event => set('use_ai', event.target.checked)} /> Usar IA</label></div>
    <p className={styles.note}>IA é opt-in. Se indisponível, o motor usa geração determinística.</p>
    {error && <div role="alert" className={styles.error}>Não foi possível gerar agora. Revise os dados e tente novamente.</div>}
    <button disabled={loading}>{loading ? 'Gerando…' : 'Gerar hooks'}</button>
  </form>;
});
