# Buffer Social Media

Integração com Buffer para postagem automática nas redes sociais do Instituto Vital Slim.

---

## Configuração

| Item | Valor |
|------|-------|
| Skill | `~/.openclaw/workspace/skills/buffer-social/` |
| Script | `scripts/post_buffer.py` |
| API Key | `/root/.openclaw/secure/buffer.env` |
| Endpoint | `https://api.buffer.com/` (GraphQL) |
| Organização | `69e90408151436756ee2629a` (Instituto Vital Slim) |

## Uso

### Criar post
```bash
cd ~/.openclaw/workspace/skills/buffer-social/
python3 scripts/post_buffer.py --text "Texto do post" --channels instagram
```

### Via OpenClaw
Usar a skill `buffer-social` ou chamar o script diretamente.

## Regras

- Buffer usa **GraphQL API** (não REST)
- Token OIDC só funciona no endpoint `api.buffer.com`
- Mutation principal: `CreateIdea`
- Sempre testar antes de agendar postagens em massa

## Status

✅ Testado e funcionando — post de teste criado com sucesso (`id: 69e9275415b2e6acbd361053`)
