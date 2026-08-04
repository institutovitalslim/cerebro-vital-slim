#!/usr/bin/env python3
import json, re, shutil
from pathlib import Path
import sys
sys.path.insert(0, '/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/scripts')
from gerar_apresentacao_v11 import render_apresentacao_v11

BASE = Path('/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/state')
OUTDIR = Path('/root/cerebro-vital-slim/deliverables')
OUTDIR.mkdir(parents=True, exist_ok=True)

bio = json.load(open(BASE/'nicelia-bioimpedancia.json'))
ant = json.load(open(BASE/'nicelia-antropometria.json'))

paciente = {
    'nome': 'Nicelia Rubem Santos de Sousa',
    'sexo': 'F',
    'idade': 62,
    'telefone': '71993254499',
    'data_consulta': '29.06.2026',
    'dataNascimento': '1964-09-10',
}

dados = {
    'telefone': '71993254499',
    'email': 'niceliarubem@hotmail.com',
    'comoConheceu': 'indicação',
    'pesoAtual': '70,7',
    'altura': '1,63',
    'queixaPrincipal': 'Peso',
    'spin_s_tempoLuta': 'Vida toda',
    'spin_s_tempoLutaDetalhe': 'Emagreço e não mantenho; volta tudo ou mais um pouco.',
    'tentativasAnteriores': 'Dieta e academia',
    'spin_p_desafios': 'Manter o peso após emagrecer e reduzir a dependência de carboidratos.',
    'spin_i_impactoVida': 'Incomoda no corpo e na autoestima.',
    'spin_i_cenario1ano': 'Tem receio de estar mais gorda se nada mudar.',
    'spin_i_investimentoPerdido': 'Já investiu em tentativas anteriores.',
    'spin_n_vidaResolvida': 'Ficar feliz, sentir o corpo menos gordo e poder comer o que gosta com menos preocupação com o peso.',
    'spin_n_interessePrograma': 'Precisa pensar',
    'interesseAcompanhamento': 'Mensal',
    'tresObjetivos': 'Emagrecer; manter-se magra; poder comer o que gosta sem preocupação com o peso.',
    'tresMudancas': 'Corpo menos gordo em 3 meses.',
    'medicamentosAtuais': 'Não usa medicamentos contínuos.',
    'doencasCronicas': 'Não informou doenças crônicas.',
    'cirurgias': 'Cesária',
    'reposicaoHormonal': 'Ainda não faz reposição hormonal.',
    'historicoFamiliarCancer': 'Não',
    'alergiasIntolerancias': 'Glúten',
    'habitoFumar': 'Não',
    'consumoAlcool': 'Pouco',
    'qualidadeSono': '3',
    'horasSono': 'Não informado',
    'nivelEnergia': '3',
    'cansacoDurante': 'Sim, mais pela manhã; disposição ao acordar 1/5 e no fim do dia 4/5.',
    'atividadeFisica': 'Não pratica atividade física atualmente.',
    'frequenciaAtividade': 'Nenhuma',
    'consumoAgua': '2 litros',
    'frequenciaIntestinal': 'Às vezes preso, às vezes bom.',
    'profissao': 'Do lar',
    'tipoTrabalho': 'Misto',
    'horariosTrabalho': 'Não informado',
    'barreiraSaude': 'Dinheiro',
    'investeSaude': 'Não informado',
    'consumoDoces': 'Doce pouco; carboidrato muito.',
    'refeicoesDia': '2',
    'localRefeicoes': 'Casa',
    'formaAdocar': 'Não adoça',
    'alimentosGosta': 'Frutos do mar, carboidrato, feijão, frutas, frango e peixe.',
    'alimentosNaoGosta': 'Açúcar, farinha de trigo e álcool.',
    'alimentacaoFimSemana': 'Depende',
    'alimentacaoFimSemanaDetalhe': 'Alimentação',
    'cafeDaManha': 'Pão, ovo, queijo, café, banana, tapioca.',
    'lancheManha': 'Não faz.',
    'almoco': 'Bem diversificado quando almoça; às vezes lancha.',
    'lancheTarde': 'Não faz.',
    'jantar': 'Geralmente o mesmo do café.',
    'cicloMenstrual': 'Não menstrua mais.',
    'menopausa': 'Menopausa',
    'ressecamentoVaginal': 'Não',
    'quedaCabelo': 'Sim',
    'pele': 'Seca',
}
questionario = {'pre-consulta': {'dados': dados}}

analise_questionario = {
    'interpretacao_inicial': (
        'Nicelia relata uma luta de vida toda com peso, com padrão de emagrecer e não conseguir manter, associado a sedentarismo, baixa disposição ao acordar, sono de qualidade baixa e preferência importante por carboidratos. '
        'A bioimpedância e a antropometria ajudam a orientar a consulta para redução de gordura com preservação de massa magra, enquanto os exames de sangue ainda precisam complementar a análise metabólica, hormonal e inflamatória.'
    ),
    'sinais_alerta': [
        {'sinal': 'Reganho recorrente após emagrecer', 'prioridade': 3, 'justificativa': 'História de perda e recuperação de peso sugere necessidade de estratégia de manutenção, não apenas perda pontual.'},
        {'sinal': 'Sedentarismo com objetivo de emagrecimento e manutenção', 'prioridade': 3, 'justificativa': 'A ausência de atividade física dificulta preservação de massa muscular e manutenção do resultado.'},
        {'sinal': 'Baixa disposição ao acordar e sono ruim', 'prioridade': 2, 'justificativa': 'Energia matinal muito baixa e sono 3/10 podem impactar fome, aderência e metabolismo.'},
        {'sinal': 'Menopausa com queda de cabelo e pele seca', 'prioridade': 2, 'justificativa': 'Sintomas hormonais devem ser correlacionados com avaliação médica e exames laboratoriais.'},
    ]
}

exames = {'grupos': []}
interp = {'sistemas': {}, 'alertas_criticos_globais': []}

paths = []
for versao_paciente in (False, True):
    p = render_apresentacao_v11(
        paciente=paciente,
        questionario=questionario,
        exames=exames,
        output_dir=str(OUTDIR),
        versao_paciente=versao_paciente,
        perfil_disc='D',
        bioimpedancia=bio,
        analise_questionario=analise_questionario,
        interpretacao_exames=interp,
        cruzamento=None,
    )
    paths.append(Path(p))

def fmt(v, unit=''):
    if v in (None, ''): return '—'
    if isinstance(v, float):
        s = (f'{v:.1f}' if v % 1 else f'{int(v)}').replace('.', ',')
    else:
        s = str(v).replace('.', ',')
    return f'{s} {unit}'.strip()

ant_rows = [
    ('Data da avaliação', ant.get('data'), ''),
    ('Peso', ant.get('peso_kg'), 'kg'),
    ('Altura', ant.get('altura_cm'), 'cm'),
    ('Cintura', ant.get('cintura_cm'), 'cm'),
    ('Abdômen', ant.get('abdomen_cm'), 'cm'),
    ('Pescoço', ant.get('pescoco_cm'), 'cm'),
    ('Peito', ant.get('peito_cm'), 'cm'),
    ('Braço direito', ant.get('braco_direito_cm'), 'cm'),
    ('Quadril', ant.get('quadril_cm'), 'cm'),
    ('Perna direita', ant.get('perna_direita_cm'), 'cm'),
    ('SPO₂', ant.get('spo2_pct'), '%'),
    ('Frequência cardíaca', ant.get('frequencia_cardiaca_bpm'), 'bpm'),
    ('Pressão arterial', ant.get('pressao_arterial'), ''),
]
rows_html = ''.join(f'<div class="anthro-kpi"><span>{label}</span><strong>{fmt(val, unit)}</strong></div>' for label, val, unit in ant_rows)
obs = ' '.join(ant.get('campos_incertos') or [])
if obs:
    obs = f'<p class="anthro-note"><strong>Observação de leitura:</strong> {obs}</p>'

anthro_section = f'''
<section id="antropometria" class="section anthro-section">
  <div class="wrap">
    <h2>Antropometria — medidas corporais iniciais</h2>
    <p class="lead">Registro realizado na pré-consulta. Esses dados ajudam a acompanhar a evolução de composição corporal além do peso da balança.</p>
    <div class="anthro-grid">{rows_html}</div>
    {obs}
  </div>
</section>
'''

pending_section = '''
<section id="exames-pendentes" class="section pending-labs-section">
  <div class="wrap">
    <h2>Exames de sangue — pendentes na pasta</h2>
    <div class="compact-decision" style="border-left:4px solid var(--gold);">
      <h4>O que ainda falta para fechar a leitura metabólica</h4>
      <p class="body-text">Até o momento, a pasta contém questionário, antropometria e bioimpedância. Não há PDF de exames laboratoriais de sangue disponível para esta versão.</p>
      <p class="body-text">Assim que os exames forem anexados, a análise pode ser complementada com perfil glicídico, lipídico, tireoide, vitaminas, função hepática/renal, marcadores hormonais e inflamatórios, sem alterar os dados já registrados aqui.</p>
    </div>
  </div>
</section>
'''

extra_css = '''
<style>
.anthro-section{background:linear-gradient(180deg,#fffaf0 0%,#fffdf8 100%);padding:var(--s-7) 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.anthro-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-top:var(--s-5)}
.anthro-kpi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;box-shadow:0 6px 18px rgba(88,62,32,.045)}
.anthro-kpi span{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px}
.anthro-kpi strong{font-size:22px;color:var(--ink);font-variant-numeric:tabular-nums;font-weight:650}
.anthro-note{font-size:12px;color:var(--muted);margin-top:14px;line-height:1.55}.pending-labs-section{background:#fffdf8;padding:var(--s-7) 0}
</style>
'''

final_paths=[]
for p in paths:
    html = p.read_text(encoding='utf-8')
    html = html.replace('</style>', extra_css.replace('<style>','').replace('</style>','') + '\n</style>', 1)
    if '<section id="bioimpedancia"' in html:
        html = html.replace('<section id="bioimpedancia"', anthro_section + '\n<section id="bioimpedancia"', 1)
    else:
        html = html.replace('<section id="critical-levers"', anthro_section + '\n<section id="critical-levers"', 1)
    # Insert pending labs after bioimped section, before IVS machine/program if no lab levers exist.
    marker = '<section id="ivs-machine"'
    if marker in html:
        html = html.replace(marker, pending_section + '\n' + marker, 1)
    else:
        html = html.replace('</main>', pending_section + '\n</main>', 1)
    html = html.replace('Apresentação V2', 'Apresentação V11')
    final_name = p.name.replace('-v10-', '-v11-').replace('-paciente-v10-', '-paciente-v11-')
    final = OUTDIR / final_name
    final.write_text(html, encoding='utf-8')
    final_paths.append(str(final))

print(json.dumps({'html_interna': final_paths[0], 'html_paciente': final_paths[1]}, ensure_ascii=False, indent=2))
