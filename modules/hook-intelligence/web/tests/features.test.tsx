import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, test, vi } from 'vitest';
import { HookCard } from '@/components/HookCard';
import { ComparisonTray } from '@/components/ComparisonTray';
import Library from '@/app/library/page';
import Saved from '@/app/saved/page';
import type { Hook } from '@/lib/types';

afterEach(()=>{cleanup();vi.unstubAllGlobals();vi.restoreAllMocks()});
const hook=(status:Hook['compliance']['status']='pass'):Hook=>({id:'22222222-2222-4222-8222-222222222222',text:'Um novo olhar para sono',language:'pt-BR',library:'universal',pattern_id:'universal-test',mechanisms:['curiosity_gap'],objective:'retention',channel:'reel',awareness_stage:'problem_aware',audience:'mulheres 40+',topic:'sono',tone:'premium',scores:{clarity:90,specificity:80,novelty:75,retention:88,channel_fit:92,overall:86},compliance:{status,reasons:status==='review'?['Revisar contexto']:[]},explanation:'Abre uma lacuna.',source:'deterministic',engine_version:'0.1.0',created_at:'2026-01-01T00:00:00Z'});
const response=(data:unknown,ok=true)=>Promise.resolve({ok,json:()=>Promise.resolve(data)} as Response);

describe('ações do card e comparação',()=>{
 test('BLOCK desabilita comparação e REVIEW permanece explicitamente visível',()=>{const compare=vi.fn();const {rerender}=render(<HookCard hook={hook('block')} onCompare={compare}/>);expect(screen.getByRole('button',{name:'Comparar'})).toBeDisabled();rerender(<HookCard hook={hook('review')}/>);expect(screen.getByText('Requer revisão')).toBeVisible()});
 test('favorito é idempotente, copia e adaptar envia briefing',async()=>{const fetchMock=vi.fn(()=>response({id:hook().id,favorite:true}));vi.stubGlobal('fetch',fetchMock);const writeText=vi.fn().mockResolvedValue(undefined);Object.defineProperty(navigator,'clipboard',{value:{writeText},configurable:true});const adapt=vi.fn();window.addEventListener('adapt-hook',adapt);render(<HookCard hook={hook()}/>);await userEvent.click(screen.getByRole('button',{name:'Favoritar'}));await userEvent.click(screen.getByRole('button',{name:'Favoritado'}));expect(fetchMock).toHaveBeenCalledTimes(1);await userEvent.click(screen.getByRole('button',{name:'Copiar'}));expect(writeText).toHaveBeenCalledWith(hook().text);await userEvent.click(screen.getByRole('button',{name:'Adaptar'}));expect(adapt).toHaveBeenCalledTimes(1);window.removeEventListener('adapt-hook',adapt)});
 test('tray permite remoção e limpar',async()=>{const remove=vi.fn(),clear=vi.fn();render(<ComparisonTray hooks={[hook(),{...hook(),id:'33333333-3333-4333-8333-333333333333',text:'Segundo hook'}]} onRemove={remove} onClear={clear}/>);await userEvent.click(screen.getByRole('button',{name:/Remover Um novo/}));expect(remove).toHaveBeenCalledWith(hook().id);await userEvent.click(screen.getByRole('button',{name:'Limpar'}));expect(clear).toHaveBeenCalled()});
});

describe('biblioteca e salvos',()=>{
 test('biblioteca busca, filtra e recupera de erro',async()=>{const fetchMock=vi.fn().mockImplementationOnce(()=>response({},false)).mockImplementationOnce(()=>response({},false));vi.stubGlobal('fetch',fetchMock);render(<Library/>);expect(await screen.findByRole('alert')).toBeVisible();fetchMock.mockImplementationOnce(()=>response({items:[{id:'p1',library:'universal',mechanism:'curiosity_gap',objectives:['retention'],channels:['reel'],awareness_stages:['problem_aware'],tones:['premium'],template:'Uma pergunta sobre {topic}',slots:['topic'],explanation:'Cria curiosidade',intensity:2}],total:1})).mockImplementationOnce(()=>response({taxonomies:{channels:['reel']},mechanisms:['curiosity_gap']}));await userEvent.click(screen.getByRole('button',{name:'Tentar novamente'}));expect(await screen.findByText('Uma pergunta sobre {topic}')).toBeVisible();await userEvent.type(screen.getByLabelText('Buscar padrões'),'inexistente');expect(screen.getByText('Nenhum padrão corresponde aos filtros.')).toBeVisible()});
 test('favoritos não exibem BLOCK e abas consultam paginação real',async()=>{const blocked={...hook('block'),id:'44444444-4444-4444-8444-444444444444'};const fetchMock=vi.fn((url:string)=>url.includes('/history')?response({items:[],total:0,page:1,page_size:20}):response({items:[hook(),blocked],total:2,page:1,page_size:20}));vi.stubGlobal('fetch',fetchMock);render(<Saved/>);await screen.findByText('Nenhuma sessão gerada ainda.');await userEvent.click(screen.getByRole('tab',{name:'Favoritos'}));expect(await screen.findByText(hook().text)).toBeVisible();expect(screen.queryByText(blocked.text+' bloqueado')).not.toBeInTheDocument();expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/v1/favorites?page=1&page_size=20'),expect.anything())});
});
