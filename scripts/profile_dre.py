"""Inspeção e referência independente da DRE, calculada diretamente do Excel original."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
from datetime import datetime,date
import json
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
import os,sys
# Caminho do Excel original: variável de ambiente DRE_SOURCE_XLSX (não versionar caminhos pessoais).
SOURCE=Path(os.environ.get('DRE_SOURCE_XLSX') or sys.exit('Defina DRE_SOURCE_XLSX com o caminho do BaseDados.xlsx original.'))
w=openpyxl.load_workbook(SOURCE,read_only=False,data_only=True)
tables={}
dictionary=['# Dicionário de dados — inspeção real','',
 'Inspeção recursiva do workspace, inclusive arquivos ignorados: encontrada data/processed/BaseDados_Tratada.xlsx. A fonte BaseDados.xlsx foi localizada pelo caminho das consultas existentes e também lida. Contexto Projeto.pptx e dCalendario.txt contêm requisitos/código, não movimentos financeiros.',
 'Base original preservada. Base tratada é derivada, não uma segunda fonte a somar. Valores são mensais, não notas fiscais, vendas individuais ou lançamentos bancários.']
for s in w:
    raw=list(s.values); headers=raw[0]
    meaningful=[(i,h) for i,h in enumerate(headers) if h is not None]
    rows=[dict((h,r[i] if i<len(r) else None) for i,h in meaningful) for r in raw[1:]]
    rows=[r for r in rows if any(v is not None for v in r.values())]
    tables[s.title]=rows
    purpose=('estrutura gerencial por filial' if s.title=='dEstruturaDRE' else 'cadastro/classificação das contas por filial' if s.title=='dPlanoConta' else 'orçamento mensal' if s.title=='fOrcamento' else 'previsão mensal' if s.title=='fPrevisao' else 'realizado mensal por conta; fragmento de filial/ano')
    dictionary += ['',f'## {s.title}',f'Finalidade: {purpose}. Linhas de negócio: {len(rows)}. Linhas vazias excluídas: {len(raw)-1-len(rows)}.', '', '| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |','|---|---|---:|---:|']
    for _,h in meaningful:
        values=[r[h] for r in rows]; notnull=[v for v in values if v is not None]
        kinds=','.join(sorted(set(type(v).__name__ for v in notnull)))
        target='texto' if h in ['id','planoContas_id','mascaraDRE_id'] else 'data' if h=='competencia_data' else 'inteiro' if h in ['index','subtotal','detalharN2','tipoLancamento'] else 'decimal' if h=='valor' else 'texto'
        dictionary.append(f'| {h} | {kinds} → {target} | {len(values)-len(notnull)} | {len(set(notnull))} |')
    keys=['competencia_data','planoContas_id'] if s.title.startswith('f') else ['id']
    duplicates=len(rows)-len({tuple(r[k] for k in keys) for r in rows})
    dictionary += ['',f'Chave/grão: {" + ".join(keys)}. Duplicidades: {duplicates}.']
    if s.title.startswith('f'):
        dictionary += [f'Período: {min(r["competencia_data"] for r in rows):%d/%m/%Y} a {max(r["competencia_data"] for r in rows):%d/%m/%Y}. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.']
    elif s.title=='dPlanoConta':dictionary += ['FK mascaraDRE_id → dEstruturaDRE.id. tipoLancamento determina natureza +1/-1.']
    for name,t in s.tables.items():
        # openpyxl TableList.items retorna referência textual.
        table=s.tables[name]
        dictionary += [f'Tabela Excel nomeada auxiliar `{name}`: intervalo {table.ref}; recorte desta aba, não nova fonte de fatos.']
plan={r['id']:r for r in tables['dPlanoConta']}
structure={r['id']:r for r in tables['dEstruturaDRE']}
assert len(plan)==len(tables['dPlanoConta'])
assert all(r['mascaraDRE_id'] in structure and r['tipoLancamento'] in [-1,1] for r in plan.values())
scenarios={'Realizado':[r for n,rs in tables.items() if n.startswith('fLancamento') for r in rs], 'Previsto':tables['fPrevisao'],'Orcado':tables['fOrcamento']}
reference=[]; unknown=[]; signs={}; negatives={}
for scenario,rows in scenarios.items():
    agg=defaultdict(Decimal);signs[scenario]=Counter();negatives[scenario]=0
    for r in rows:
        if r['planoContas_id'] not in plan:unknown.append((scenario,r['planoContas_id']));continue
        p=plan[r['planoContas_id']];group=int(p['mascaraDRE_id'].split('.')[1]);branch=r['planoContas_id'].split('.')[0]
        raw=Decimal(str(r['valor']));signed=raw*Decimal(str(p['tipoLancamento']))
        signs[scenario][str(group)+(' negativo' if raw<0 else ' positivo' if raw>0 else ' zero')]+=1
        negatives[scenario]+=int(raw<0)
        key=(r['competencia_data'].year,r['competencia_data'].month,branch,group)
        agg[key]+=signed
    for (year,month,branch,group),value in agg.items():reference.append({'cenario':scenario,'ano':year,'mes':month,'filial':branch,'grupo':group,'valor':str(value)})
assert not unknown, 'Movimentos sem conta'
assert {r['grupo'] for r in reference}=={1,2,4,6,7,9,10,12}
out=ROOT/'artifacts/dre';out.mkdir(parents=True,exist_ok=True)
(out/'reference.json').write_text(json.dumps(reference,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'quality.json').write_text(json.dumps({'unclassified':unknown,'negative_raw':negatives,'signs':signs},ensure_ascii=False,indent=2),encoding='utf-8')
dictionary += ['', '## Tabelas derivadas e de apresentação',
 '- fLancamentos: união das nove fontes de realizado; 3.741 registros, grão mensal/conta. Não somar suas origens novamente.',
 '- dFilial: 3 chaves textuais, nomes obtidos de empresa da estrutura: 01 São Paulo, 02 Rio de Janeiro, 03 Florianópolis.',
 '- dCalendario: 1.095 dias, 2021–2023; Data única, Ano/MesNum/AnoMesINT inteiros, nomes textuais pt-BR e atributos de ordenação. Sem FK; dimensão no lado 1.',
 '- dDRE: linhas de apresentação, desconectada; medidas selecionam os grupos originais, sem somar linhas calculadas.',
 '- dPeriodo: seletor desconectado de contexto, YTD e ano completo; utilizado apenas pelas medidas da matriz.',
 '', '## Qualidade e classificação',
 f'- Movimentos sem classificação: {len(unknown)}. Contas sem máscara: zero. Sinais da natureza do plano: somente -1 e +1.',
 f'- Valores brutos negativos: {negatives}. Preservados e multiplicados pela natureza; não aplicar ABS aos movimentos.',
 '- As 15 descrições vazias de dEstruturaDRE são subtotais marcados por subtotal=1. Seus rótulos gerenciais são explicitados nas regras; não representam contas desconhecidas.',
 '- Na importação anterior, códigos haviam virado datas e linhas vazias eram carregadas. A base tratada corrige esses problemas.']
(ROOT/'docs/dicionario-dados.md').write_text('\n'.join(dictionary)+'\n',encoding='utf-8')
print('Referência independente:',len(reference),'agregados mês/filial/grupo; não classificados:',len(unknown));print('Negativos preservados:',negatives)
