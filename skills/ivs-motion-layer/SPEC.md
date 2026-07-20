# SPEC-IVS-MOTION-LAYER-20260720

## Goal
Criar uma camada reutilizável para aplicar animações premium em apresentações HTML, sites e landing pages do IVS usando Lenis, GSAP e Vanta de forma governada, com componentes próprios inspirados visualmente em React Bits sem copiar código.

## Acceptance Criteria
- [x] Ter CSS e JS reutilizáveis que funcionem em HTML estático.
- [x] Lenis deve ser carregado de forma opcional para scroll suave.
- [x] GSAP deve animar seções, cards, counters e linhas de progresso quando disponível.
- [x] Vanta deve ser opcional e restrito a hero/background com fallback.
- [x] Respeitar `prefers-reduced-motion` e `data-ivs-motion="off"`.
- [x] Ter CLI para aplicar a camada em um HTML existente sem sobrescrever por padrão.
- [x] Ter demo real de apresentação IVS validável no navegador.
- [x] Ter testes mínimos para injeção, estrutura e ausência de secrets/PII.

## Scope
- **In scope:** camada local CSS/JS, CLI de aplicação, demo, testes e documentação de uso.
- **Out of scope:** publicar site externo, enviar a paciente/lead, alterar geradores V10/V11 existentes, copiar código de React Bits.

## Technical Approach
Implementação IVS-first em arquivos estáticos:
- `assets/ivs-motion.css` — tokens, estados iniciais, fallbacks, reduced-motion.
- `assets/ivs-motion.js` — loader governado de CDN, inicialização de Lenis/GSAP/Vanta, presets próprios.
- `scripts/apply_motion.py` — injeta CSS/JS e marcações em HTML.
- `examples/demo-apresentacao-ivs-motion.html` — demo real.

## Log Points
- `apply_motion.py`: INFO no início/fim, WARN quando HTML já possui a camada, ERROR em arquivo inexistente.

## TRUST 5 Checklist
- [x] **Tested:** testes e smoke real executados.
- [x] **Readable:** arquivos claros e documentados.
- [x] **Unified:** design system IVS e governança de motion.
- [x] **Secured:** sem tokens, sem PII, sem envio externo.
- [x] **Trackable:** documentação, relatório de teste e evidências.
