---
name: ivs-motion-layer
description: Aplica animações premium governadas em apresentações HTML, sites e landing pages do IVS usando Lenis, GSAP, Vanta opcional e presets IVS-first próprios.
---

# IVS Motion Layer

Use quando Maria, João ou Tiaro quiserem transformar HTMLs estáticos do IVS em apresentações/sites com motion premium, mantendo clareza médica, performance e governança.

## Comando principal

```bash
python3 /root/cerebro-vital-slim/skills/ivs-motion-layer/scripts/apply_motion.py \
  <entrada.html> \
  --out <saida-motion.html> \
  --profile presentation \
  --vanta
```

Perfis:

| Profile | Uso |
|---|---|
| `presentation` | V10/V11, evolução, relatórios executivos |
| `landing` | landing page/site comercial |
| `minimal` | só CSS/JS e reduced-motion, sem Vanta |

## Critério de aceite

- HTML abre localmente.
- Seções marcadas recebem `data-ivs-motion`.
- Reduced motion funciona.
- Nenhum dado sensível é inserido.
- Vanta só aparece se `--vanta` ou elemento com `data-ivs-vanta` existir.

## Pitfalls

- GSAP tem licença própria; manter como dependência governada.
- React Bits tem Commons Clause; não copiar componentes.
- Vanta/Three podem pesar; usar apenas em hero e com fallback.
