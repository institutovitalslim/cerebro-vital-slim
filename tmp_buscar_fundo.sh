#!/bin/bash
# Buscar fundo contextual no Unsplash
curl -s -L "https://source.unsplash.com/1080x810/?laboratory,microscope,medical,research" \
  -o /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/fundo_temp.jpg 2>&1
file /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/fundo_temp.jpg
ls -la /root/cerebro-vital-slim/deliverables/glp1-cancer-endometrial/corrigido/fundo_temp.jpg
