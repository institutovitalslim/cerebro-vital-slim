# Fotos Dra. Daniely — Banco de Imagens

Todas as fotos: fundo escuro (cinza/preto), estúdio profissional.

| Arquivo | Descrição | Melhor uso |
|---------|-----------|------------|
| `daniely-01-bracoscruzados.png` | Braços cruzados, blusa branca/amarela, calça mostarda | Capa de carrossel, autoridade |
| `daniely-02-caneta.png` | Segurando caneta na direção da câmera, blusa branca/amarela | Reel, CTA direto |
| `daniely-03-biomeds.png` | Segurando caixa Biomeds (medicamentos), blusa branca/amarela | Posts sobre tratamentos, GLP-1 |
| `daniely-04-blazer-branco-curta.png` | Blazer branco (mãos na frente, postura elegante) — corte mais fechado | Perfil, avatar, capa premium |
| `daniely-05-blazer-branco-longa.png` | Blazer branco (foto inteira, saia longa) — postura elegante | Slide de abertura, capa institucional |

## Uso no avatar (tweet carrossel)
Para gerar avatar circular do script `make_tweet_slides.py`:
```python
from PIL import Image
img = Image.open("daniely-04-blazer-branco-curta.png")
# Recortar rosto (ajustar coords conforme necessário)
avatar = img.crop((350, 50, 750, 450))
avatar.save("avatar.png")
```

_Atualizado: 2026-04-06_
