# SPEC-CEOS-AVATAR-001: Pilares estratégicos derivados do Avatar Mestre IVS

## Fonte
Documento enviado pelo Tiaro: `Avatar Mestre - Instituto Vital Slim.docx`.

## Avatar central
**A mulher que não se reconhece mais no espelho**: mulher 30–45, sobrepeso/obesidade inicial, alta urgência emocional, perda de controle do corpo após gravidez, pandemia, estresse, ansiedade, rotina intensa ou transição hormonal.

## Linguagem mental usada como base
- “Meu corpo não responde.”
- “Já tentei de tudo.”
- “Não consigo parar de comer doce.”
- “Depois dos filhos tudo mudou.”
- “Não me reconheço mais.”
- “Tenho baixo desejo sexual.”

## Desejo central
Esperança de voltar a ser quem era, com reconexão da identidade feminina, autoestima e controle do corpo.

## Pilares adicionados ao Sprint Semanal
1. Reconexão com identidade feminina
2. Corpo não responde
3. Já tentei de tudo
4. Depois dos filhos tudo mudou
5. Compulsão por açúcar e controle
6. Gordura abdominal e metabolismo
7. Energia, cansaço e rotina
8. Libido, autoestima e hormônios
9. Menopausa e metabolismo
10. Medo do efeito sanfona
11. Executiva sobrecarregada
12. Segurança médica e valor

## Governança de copy
- Não prometer resultado.
- Não diagnosticar por conteúdo.
- Não expor sexualidade/libido de forma vulgar.
- Não culpar a paciente.
- Não usar “falta de força de vontade” como acusação; usar como reframe.
- Mostrar método, avaliação e acompanhamento antes de preço.

## Uso no Content Engine OS
Os pilares alimentam `/sprint-semanal` via API:

```text
GET /api/weekly-command/overview?tenant_slug=demo
```

Cada pilar devolve:
- `pillar`
- `label`
- `thesis`
- `objection`
- `promise_safe`

A tese escolhida gera família de conteúdo:
- Reels
- Carrossel
- Stories
- Estático
