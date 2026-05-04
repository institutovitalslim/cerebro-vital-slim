# Template: Onboarding pos pre-consulta paga

Disparado quando lead paga R$ 300 da pre-consulta + agendamento confirmado.

Caso real: Mario Abreu Gomes Filho (28/04/2026 - fluxo completo capturado).

## Sequencia em blocos

```
[BLOCO 1] Saudacao
Bom dia, [Nome]! 💚

[delay 2s]

[BLOCO 2] Apresentacao com upgrade
Aqui e a Liane, enfermeira chefe e responsavel pelo sucesso do paciente 
do Instituto Vital Slim, e acabamos de agendar a sua consulta.
[OU se foi indicacao familiar: ...a pedido de [familiar]]

[delay 1.5s]

[BLOCO 3] Confirmacao data/hora "em ponto"
O seu atendimento esta marcado no dia [DD/MM] ([dia da semana]) 
as [HH:MM]h em ponto. Ok?

[aguarda confirmacao paciente]

[BLOCO 4] Endereco completo
Nosso endereco e Rua Priscila B. Dutra, 389, Estacao Villas Shopping, 
sala 305, Buraquinho, Lauro de Freitas - BA, 42709-200.
https://maps.app.goo.gl/ADT3m3rqTKM7Q3oV6

[delay 2s]

[BLOCO 5] Logistica - roupa
Neste dia, venha com uma roupa confortavel, preferencialmente de 
academia se possivel.

[delay 1.5s]

[BLOCO 6] Logistica - tempo
E venha com tempo disponivel para que a sua consulta dure o tempo 
que precisar.

[delay 2s]

[BLOCO 7] 🎬 Video Boas-Vindas (40 MB)
Segue um recado da Dra. Daniely para voce 👇
[anexar BOAS VINDAS.mp4]

[delay 3s]

[BLOCO 8] Pedido de exames
Voce possui exames de sangue recentes? Se sim, voce consegue nos 
disponibilizar o resultado por PDF? Assim anexaremos ao seu 
prontuario eletronico.

[aguarda resposta]

[BLOCO 9] Questionario
Para que possamos oferecer um atendimento ainda mais personalizado e 
eficiente, convidamos voce a preencher este questionario:
preconsulta.institutovitalslim.com.br

O preenchimento e muito importante para podermos lhe oferecer o 
melhor atendimento possivel.

[delay 2s]

[BLOCO 10] Acompanhamento
Me sinaliza assim que finalizar o preenchimento do questionario, 
combinado? 📋
```

## Variacoes

### Se paciente ja enviou exames antes
Pular BLOCO 8.

### Se paciente nao tem exames recentes
"Tudo bem. Na consulta a Dra. ja vai prescrever os exames necessarios."

### Sistema antigo (Google Forms) - DEPRECATED
Nao usar mais Google Forms. Usar `preconsulta.institutovitalslim.com.br` (RC-22).

## Tom

Acolhedor, organizado, profissional. Cada bloco tem 1 ideia. Pausas naturais. Nao mistura logistica + emocional.

## NAO incluir

- Valores
- Cashback (so foi mencionado pre-pagamento)
- Detalhes do programa
