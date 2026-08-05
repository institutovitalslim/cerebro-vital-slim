'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { GenerationPayload, GenerationResponse } from '@/lib/types';
import styles from './GeneratorForm.module.css';
const split=(value:string)=>value.split(',').map(v=>v.trim()).filter(Boolean);
const initial:GenerationPayload={topic:'',audience:'',library:'universal',channel:'reel',objective:'retention',awareness_stage:'problem_aware',tone:'premium',intensity:2,mechanism:null,context:null,required_words:[],forbidden_words:[],count:12,max_length:180,use_ai:false};
export function GeneratorForm({onResult}:{onResult:(value:GenerationResponse)=>void}){
 const [form,setForm]=useState(initial); const [required,setRequired]=useState(''); const [forbidden,setForbidden]=useState(''); const [loading,setLoading]=useState(false); const [error,setError]=useState(false);
 useEffect(()=>{const adapt=(event:Event)=>{const hook=(event as CustomEvent<{topic:string;text:string}>).detail;setForm(v=>({...v,topic:hook.topic,context:`Adaptar com base neste rascunho: ${hook.text}`}));document.getElementById('topic')?.focus();};window.addEventListener('adapt-hook',adapt);return()=>window.removeEventListener('adapt-hook',adapt)},[]);
 const set=<K extends keyof GenerationPayload>(key:K,value:GenerationPayload[K])=>setForm(v=>({...v,[key]:value}));
 async function submit(e:React.FormEvent){e.preventDefault();setLoading(true);setError(false);try{onResult(await api.generate({...form,required_words:split(required),forbidden_words:split(forbidden)}));}catch{setError(true)}finally{setLoading(false)}}
 return <form className={styles.form} onSubmit={submit} aria-label="Briefing do gerador">
  <div className={styles.heading}><span>01 / Briefing</span><h2>Direção editorial</h2></div>
  <label>Tema<input id="topic" required minLength={2} value={form.topic} onChange={e=>set('topic',e.target.value)}/></label>
  <label>Público<input required minLength={2} value={form.audience} onChange={e=>set('audience',e.target.value)}/></label>
  <div className={styles.two}><label>Biblioteca<select value={form.library} onChange={e=>set('library',e.target.value as GenerationPayload['library'])}><option value="universal">Universal</option><option value="ivs-health">IVS Health</option></select></label><label>Canal<select value={form.channel} onChange={e=>set('channel',e.target.value)}><option value="reel">Reel</option><option value="carousel">Carrossel</option><option value="story">Story</option><option value="email">E-mail</option><option value="youtube">YouTube</option><option value="blog">Blog</option><option value="ad">Anúncio</option><option value="landing_page">Landing page</option></select></label></div>
  <div className={styles.two}><label>Objetivo<select value={form.objective} onChange={e=>set('objective',e.target.value)}><option value="retention">Retenção</option><option value="curiosity">Curiosidade</option><option value="education">Educação</option><option value="authority">Autoridade</option><option value="identification">Identificação</option><option value="action">Ação</option></select></label><label>Consciência<select value={form.awareness_stage} onChange={e=>set('awareness_stage',e.target.value)}><option value="unaware">Inconsciente</option><option value="problem_aware">Ciente do problema</option><option value="solution_aware">Ciente da solução</option><option value="product_aware">Ciente do produto</option><option value="ready_to_act">Pronto para agir</option></select></label></div>
  <div className={styles.two}><label>Tom<select value={form.tone} onChange={e=>set('tone',e.target.value)}><option value="premium">Premium</option><option value="educational">Educativo</option><option value="direct">Direto</option><option value="empathetic">Empático</option><option value="provocative">Provocativo</option></select></label><label>Intensidade<select value={form.intensity} onChange={e=>set('intensity',Number(e.target.value))}><option value="1">Sutil</option><option value="2">Equilibrada</option><option value="3">Alta</option></select></label></div>
  <label>Mecanismo<input value={form.mechanism??''} onChange={e=>set('mechanism',e.target.value||null)} placeholder="Opcional: curiosity_gap"/></label>
  <label>Contexto<textarea value={form.context??''} onChange={e=>set('context',e.target.value||null)} rows={3}/></label>
  <div className={styles.two}><label>Palavras obrigatórias<input value={required} onChange={e=>setRequired(e.target.value)} aria-describedby="words-help"/></label><label>Palavras proibidas<input value={forbidden} onChange={e=>setForbidden(e.target.value)}/></label></div><small id="words-help">Separe termos por vírgulas.</small>
  <div className={styles.three}><label>Quantidade<input type="number" min={1} max={50} value={form.count} onChange={e=>set('count',Number(e.target.value))}/></label><label>Máx. caracteres<input type="number" min={30} max={280} value={form.max_length} onChange={e=>set('max_length',Number(e.target.value))}/></label><label className={styles.check}><input type="checkbox" checked={form.use_ai} onChange={e=>set('use_ai',e.target.checked)}/> Usar IA</label></div>
  <p className={styles.note}>IA é opt-in. Se indisponível, o motor usa geração determinística.</p>
  {error&&<div role="alert" className={styles.error}>Não foi possível gerar agora. Revise os dados e tente novamente.</div>}
  <button disabled={loading}>{loading?'Gerando…':'Gerar hooks'}</button>
 </form>
}
