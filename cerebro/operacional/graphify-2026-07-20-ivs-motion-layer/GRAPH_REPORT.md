# Graphify RC-25 — IVS Motion Layer

## Status
RC-25 operacional criado para registrar a incorporação governada dos repositórios de animação analisados a uma camada própria do IVS.

## Origem
- Pedido do Tiaro: implementar os repositórios do Reel para uso em apresentações.
- Reel analisado: `https://www.instagram.com/reel/Da3O00jpo3R/`
- Relatório consolidado: `/root/.openclaw/reports/repo-reverse-ivs/20260720-ivs-motion-animation-repos-consolidado.html`

## Decisão canônica
Criar e usar a skill/camada `ivs-motion-layer` como porta única para aplicar motion premium em apresentações HTML, sites e landing pages do IVS.

## Referências incorporadas
- `darkroomengineering/lenis`: scroll suave e storytelling vertical.
- `greensock/GSAP`: timelines, counters, cards, scroll reveal e microinterações.
- `tengbao/vanta`: backgrounds 3D opcionais e pontuais.
- `DavidHDev/react-bits`: inspiração visual apenas; não copiar nem redistribuir componentes por causa de MIT + Commons Clause.

## Artefatos criados
- Skill: `/root/cerebro-vital-slim/skills/ivs-motion-layer/SKILL.md`
- README: `/root/cerebro-vital-slim/skills/ivs-motion-layer/README.md`
- SPEC: `/root/cerebro-vital-slim/skills/ivs-motion-layer/SPEC.md`
- CSS: `/root/cerebro-vital-slim/skills/ivs-motion-layer/assets/ivs-motion.css`
- JS: `/root/cerebro-vital-slim/skills/ivs-motion-layer/assets/ivs-motion.js`
- CLI: `/root/cerebro-vital-slim/skills/ivs-motion-layer/scripts/apply_motion.py`
- Demo: `/root/cerebro-vital-slim/skills/ivs-motion-layer/examples/demo-apresentacao-ivs-motion.html`
- Screenshot de validação: `/root/cerebro-vital-slim/skills/ivs-motion-layer/examples/demo-apresentacao-ivs-motion.png`

## Governança
- Motion deve priorizar clareza, leitura e sofisticação discreta.
- Reduced motion obrigatório.
- Vanta/WebGL apenas em hero/capas; fallback estático obrigatório.
- GSAP é dependência governada por licença própria.
- React Bits não deve ser copiado; usar apenas como catálogo de ideias.
- Nenhum envio externo/publicação automática é autorizado por esta skill.

## Evidência de validação
Comandos executados:

```bash
python3 -m py_compile /root/cerebro-vital-slim/skills/ivs-motion-layer/scripts/apply_motion.py
node --check /root/cerebro-vital-slim/skills/ivs-motion-layer/assets/ivs-motion.js
python3 -m unittest discover -s /root/cerebro-vital-slim/skills/ivs-motion-layer/tests -v
/snap/bin/chromium --headless --no-sandbox --disable-gpu --window-size=1440,1100 --screenshot=/root/cerebro-vital-slim/skills/ivs-motion-layer/examples/demo-apresentacao-ivs-motion.png file:///root/cerebro-vital-slim/skills/ivs-motion-layer/examples/demo-apresentacao-ivs-motion.html
```

Resultado:
- `py_compile`: OK
- `node --check`: OK
- `unittest`: 3 testes OK
- Chromium screenshot: arquivo PNG gerado com 310.907 bytes

## Próxima ação
Aplicar em um HTML real de apresentação V10/V11/evolução ou landing do IVS e avaliar com Tiaro antes de tornar padrão automático nos geradores.
