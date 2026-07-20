# IVS Motion Layer

Camada de animação premium para apresentações HTML, sites e landing pages do Instituto Vital Slim.

## O que foi incorporado dos repositórios analisados

| Referência | Uso na camada IVS | Governança |
|---|---|---|
| Lenis | scroll suave e narrativa vertical | MIT; dependência opcional via CDN |
| GSAP | timeline, cards, counters, scroll reveal | licença standard no charge; uso governado |
| Vanta | background 3D pontual em hero | MIT; só quando `data-ivs-vanta` estiver presente |
| React Bits | inspiração visual de microinterações | não copiamos componentes; presets próprios IVS-first |

## Uso rápido em HTML existente

```bash
python3 /root/cerebro-vital-slim/skills/ivs-motion-layer/scripts/apply_motion.py \
  entrada.html \
  --out saida-motion.html \
  --profile presentation \
  --vanta
```

Por padrão o script **não sobrescreve** o arquivo de entrada. Para sobrescrever, usar `--overwrite` explicitamente.

## Marcação recomendada

```html
<section class="ivs-section" data-ivs-motion="fade-up">
  <h2 data-ivs-motion="split-title">Título</h2>
  <div class="ivs-card" data-ivs-motion="card">...</div>
  <strong data-ivs-counter="21.6" data-suffix=" kg">0</strong>
</section>
```

## Presets disponíveis

- `fade-up`: entrada elegante de seção.
- `card`: elevação leve de cards.
- `split-title`: revela título por palavras.
- `counter`: via atributo `data-ivs-counter`.
- `progress`: barras com `data-ivs-progress="72"`.
- `ambient`: hero com Vanta opcional quando há `data-ivs-vanta`.

## Regras de governança

1. Motion deve ajudar clareza, não competir com conteúdo médico.
2. `prefers-reduced-motion` desativa animações não essenciais.
3. Vanta/WebGL só em hero/capa, nunca em tabela clínica densa.
4. Não usar efeitos que pareçam promessa de resultado.
5. Não enviar/publicar sem revisão humana.
6. Não copiar componentes React Bits; criar equivalentes IVS próprios.

## Demo

Abra:

`examples/demo-apresentacao-ivs-motion.html`

## Testes

```bash
python3 -m unittest discover -s /root/cerebro-vital-slim/skills/ivs-motion-layer/tests -v
```
