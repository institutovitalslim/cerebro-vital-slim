---
name: clara-learning-orchestrator
description: Orquestra a rotina diária de aprendizado da Clara com Instagram, YouTube e X/Twitter e transforma fontes externas em ações de WhatsApp.
---

# clara-learning-orchestrator

Use para executar os slots de aprendizado da Clara:

```bash
python3 /root/.openclaw/workspace/skills/clara-learning-orchestrator/scripts/clara_learning.py slot --slot instagram_manha
python3 /root/.openclaw/workspace/skills/clara-learning-orchestrator/scripts/clara_learning.py slot --slot youtube
python3 /root/.openclaw/workspace/skills/clara-learning-orchestrator/scripts/clara_learning.py slot --slot x_twitter
python3 /root/.openclaw/workspace/skills/clara-learning-orchestrator/scripts/clara_learning.py slot --slot instagram_tarde
python3 /root/.openclaw/workspace/skills/clara-learning-orchestrator/scripts/clara_learning.py slot --slot revisao
```

Saídas são salvas em `/root/.openclaw/reports/clara-learning/`.
