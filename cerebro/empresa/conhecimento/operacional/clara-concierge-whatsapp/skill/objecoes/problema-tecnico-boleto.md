# Objecao: "Nao consigo abrir o boleto / problema tecnico"

Paciente reporta dificuldade tecnica (boleto nao abre, link expirado, pagamento falhou, sistema travou).

Caso real: Larissa - "Eu consegui ate abrir o site, mas nao consegui abrir nenhum boleto. O unico documento que abriu foi o recibo." Resposta da Liane: "Disponha". ❌ NAO RESOLVEU.

## ⚠️ Pre-condicoes

Geralmente vem de PACIENTE em programa. Aplicar RC-12: Clara nao responde paciente normalmente.

MAS: detectar palavras-gatilho (`nao consegui`, `nao abriu`, `erro`, `duvida sobre boleto/pagamento`) e ESCALAR IMEDIATO via RC-19 (paralelo) - tratamento NAO-financeiro/operacional.

## Resposta da Clara (acolhimento + escalacao)

```
[BLOCO 1]
[Nome], que situacao chata. Lamento muito! 

[delay 2s]

[BLOCO 2]
Vou acionar agora a equipe para resolver isso o mais rapido 
possivel.

[delay 1.5s]

[BLOCO 3]
Em instantes alguem da equipe entra em contato com voce 
pra te enviar o boleto/link de outra forma.
```

## Notificacao paralela 🚨 RC-19 → Tiaro + Liane

```
🚨 PROBLEMA TECNICO REPORTADO

Paciente: [Nome]
WhatsApp: [+55 71 ...]
Etiqueta: [Paciente / VIP / Programa]
Hora: [HH:MM]

Reporte literal do paciente:
"[citacao]"

Categoria: erro tecnico (boleto/pagamento/link)

Acolhimento ja enviado por Clara.
Por favor, alguem reenvie o documento ou gere alternativa.
```

## Apos humano resolver

Paciente provavelmente recebe boleto direto da equipe. Clara nao precisa fechar a conversa.

Se equipe pedir Clara enviar a confirmacao:
```
[BLOCO 1]
[Nome], a equipe me confirmou que o boleto foi enviado 
novamente. 

[BLOCO 2]
Tudo certo agora?
```

## Variante: pagamento falhou

```
[BLOCO 1]
Que pena, [Nome]. Acontece.

[BLOCO 2]
Vou pedir pra equipe gerar um novo link de pagamento 
pra voce em instantes.

[BLOCO 3]
Em paralelo, se quiser tentar Pix em vez de cartao, 
tambem podemos.
```

## Variante: link de pagamento expirado

```
[BLOCO 1]
[Nome], desculpa o transtorno.

[BLOCO 2]
Vou pedir pra equipe gerar um novo link agora.

[BLOCO 3]
Em instantes te envio.
```

## NAO fazer

❌ "Disponha" sem resolver (caso Larissa - nao resolveu, ficou travada)
❌ Mandar paciente "tentar novamente" sem alternativa
❌ Pedir paciente entrar em contato com Tiaro direto (Clara que faz handoff)
❌ Ignorar o problema e seguir conversa normal

## Casos comuns

### Boleto Inter nao abre
"Vou pedir pra equipe te enviar o PDF direto aqui."

### App do banco trava
"Pode tentar pelo navegador no computador? Se nao funcionar, geramos novo link."

### Cartao recusado
"Vou pedir pra equipe gerar um link de outra forma (Pix, outro cartao, etc)."

### Recibo veio mas boleto nao
"Vou alinhar com o financeiro pra reenviar somente o boleto faltante."

## Logging

- timestamp do problema
- tipo de problema (boleto/pagamento/link/sistema)
- texto literal do paciente
- timestamp da escalacao Tiaro+Liane
- timestamp da resolucao
- documento reenviado (se aplicavel)

## Source of truth

Caso Larissa na MEMORIA_CONSOLIDADA. RC-19 (escalacao paralela nao-financeira).
