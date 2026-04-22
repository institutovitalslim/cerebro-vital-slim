from pathlib import Path
import shutil, subprocess, json
root=Path('/root/cerebro-vital-slim/deliverables/carrosseis-aprovados-2026-04-13')
mag=root/'magnesio'; cre=root/'creatina'
mag.mkdir(parents=True, exist_ok=True); cre.mkdir(parents=True, exist_ok=True)
# fallback: reuse generated doctor base for creatina because dedicated generation failed
shutil.copy('/root/.openclaw/media/tool-image-generation/magnesio_foto_dra---4f79624d-03ba-47c2-87dc-481117734a52.png', cre/'foto_dra_tmp.png')
subprocess.run([
 'python3','/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py',
 '--foto','/root/.openclaw/media/tool-image-generation/magnesio_foto_dra---4f79624d-03ba-47c2-87dc-481117734a52.png',
 '--circulo','/root/.openclaw/media/tool-image-generation/magnesio_circulo---fae30b99-7371-41c5-ad91-87c9db795b1e.png',
 '--headline',"SEU MAGNÉSIO ESTÁ|'NORMAL'|MAS SEU CORPO|DISCORDA.",
 '--destaques','MAGNÉSIO,NORMAL,DISCORDA.',
 '--out',str(mag/'slide_01.png')
], check=True)
subprocess.run([
 'python3','/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py',
 '--foto',str(cre/'foto_dra_tmp.png'),
 '--circulo','/root/.openclaw/media/tool-image-generation/creatina_circulo---f0b9441c-7f97-41f3-a953-b80a6939ff5f.png',
 '--headline','UM DOS SUPLEMENTOS|MAIS SUBESTIMADOS|PARA O CÉREBRO',
 '--destaques','SUBESTIMADOS,CÉREBRO',
 '--out',str(cre/'slide_01.png')
], check=True)
# tweet slides
mag_slides=[
 {"num":3,"paragraphs":["E isso não é raro.","2,4 BILHÕES de pessoas no mundo não consomem magnésio o suficiente.","Mas o que isso causa no seu corpo? →"]},
 {"num":4,"paragraphs":["O que a falta de magnésio causa:","→ Cãibras e fadiga","→ Insônia","→ Alterações de humor","→ Piora metabólica","E se existisse um jeito de investigar isso de verdade? →"]},
 {"num":5,"paragraphs":["Na Vital Slim, não confiamos só no exame.","1 Contexto clínico","2 Sintomas","3 Alimentação","4 Sinais do corpo","Resultado não é sorte. É precisão clínica. →"]},
 {"num":6,"paragraphs":["Seu corpo já está pedindo ajuda.","Pare de adivinhar o que falta — descubra com precisão.","[QUERO MINHA AVALIAÇÃO]","Mande MAGNÉSIO no direct →"]}
]
cre_slides=[
 {"num":3,"paragraphs":["Esta revisão analisou 16 estudos clínicos randomizados.","Ao todo, foram 492 participantes, com idades entre 20,8 e 76,4 anos.","Não foi um estudo isolado. →"]},
 {"num":4,"paragraphs":["Os pesquisadores encontraram melhora significativa na memória.","Isso significa mais facilidade para guardar e recuperar informações.","E esse foi um dos achados mais consistentes da análise. →"]},
 {"num":5,"paragraphs":["Também houve melhora no tempo de atenção.","Na prática, isso sugere um cérebro mais rápido para responder e sustentar foco.","Especialmente em tarefas mentais mais exigentes. →"]},
 {"num":6,"paragraphs":["Outro ponto importante foi a melhora na velocidade de processamento.","Ou seja, o cérebro conseguiu lidar melhor com a informação em menos tempo.","Isso importa muito no raciocínio do dia a dia. →"]},
 {"num":7,"paragraphs":["Os melhores resultados apareceram principalmente em mulheres, em pessoas entre 18 e 60 anos e em pacientes com alguma condição de saúde.","Ou seja, o efeito não apareceu de forma aleatória. →"]},
 {"num":8,"paragraphs":["Em todos os estudos incluídos, a forma usada foi a creatina monohidratada.","Isso reforça que estamos falando da forma mais estudada da creatina.","E não de uma promessa genérica. →"]},
 {"num":9,"paragraphs":["A conclusão não é que creatina faz milagre.","A conclusão é outra: ela pode ajudar memória, atenção e velocidade mental quando existe indicação correta. →"]},
 {"num":10,"paragraphs":["Estamos falando de um suplemento que muita gente associa apenas à força muscular.","Mas a pesquisa mostra que ele também pode apoiar o funcionamento do cérebro.","E isso merece mais atenção.","Se este conteúdo fez sentido para você, salve este post."]}
]
(mag/'slides.json').write_text(json.dumps(mag_slides, ensure_ascii=False, indent=2))
(cre/'slides.json').write_text(json.dumps(cre_slides, ensure_ascii=False, indent=2))
subprocess.run(['python3','/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py','--config',str(mag/'slides.json'),'--avatar','/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png','--out',str(mag),'--name','Dra. Daniely Freitas','--handle','@dradaniely.freitas'], check=True)
subprocess.run(['python3','/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py','--config',str(cre/'slides.json'),'--avatar','/root/.openclaw/media/inbound/avatar_dradaniely_oficial.png','--out',str(cre),'--name','Dra. Daniely Freitas','--handle','@dradaniely.freitas'], check=True)
print('ok')
