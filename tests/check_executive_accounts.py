"""Impactos por conta e insight de despesa conciliados diretamente ao Excel original."""
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
import json,sys
R=Path(__file__).resolve().parents[1];A=R/'artifacts/executivo'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
if '--prepare' in sys.argv:
 import openpyxl
 import os
 src=os.environ.get('DRE_SOURCE_XLSX') or sys.exit('Defina DRE_SOURCE_XLSX com o caminho do BaseDados.xlsx original.')
 w=openpyxl.load_workbook(src,read_only=True,data_only=True)
 def rows(sheet):
  it=iter(w[sheet].values);h=next(it);return [dict(zip(h,r)) for r in it if any(x is not None for x in r)]
 plan={r['id']:r for r in rows('dPlanoConta')};actual=[r for s in w.sheetnames if s.startswith('fLancamento') for r in rows(s)]
 coverage={r['competencia_data'] for r in actual};values=defaultdict(Decimal);expenses=defaultdict(Decimal)
 for sign,rs in [(1,actual),(-1,rows('fOrcamento'))]:
  for r in rs:
   if r['competencia_data'] not in coverage:continue
   p=plan[r['planoContas_id']];v=Decimal(str(r['valor']))*Decimal(str(p['tipoLancamento']))*sign;n=p['descricaoN2'];values[n]+=v
   if int(p['mascaraDRE_id'].split('.')[1])==6:expenses[n]+=v
 w.close();ranks={v:i+1 for i,v in enumerate(sorted(set(abs(v) for v in values.values()),reverse=True))}
 expected={n:{'value':str(v),'rank':ranks[abs(v)]} for n,v in values.items()}
 expected['__worst_expense__']=min(expenses,key=lambda n:(expenses[n],n))
 (A/'account-reference.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2),encoding='utf-8')
 (A/'account.dax').write_text('EVALUATE SUMMARIZECOLUMNS(dPlanoConta[descricaoN2],"Impacto",[DRE Impacto Conta R$],"Ranking",[Ranking Impacto Conta],"Top8",[Top 8 Impacto Conta])',encoding='utf-8')
 (A/'insight.dax').write_text('EVALUATE ROW("Despesa",[Insight Despesa],"Receita",[Insight Receita],"Custos",[Insight Custos])',encoding='utf-8');sys.exit()
expected=read(A/'account-reference.json');actual=read(A/'account.json');assert len(actual)==len(expected)-1
top=0
for r in actual:
 e=expected[r['dPlanoConta[descricaoN2]']];v=Decimal(e['value']);assert abs(float(v)-r['[Impacto]'])<.01
 assert r['[Ranking]']==e['rank'];assert (r['[Top8]'] is not None)==(e['rank']<=8)
 if r['[Top8]'] is not None:assert abs(float(v)-r['[Top8]'])<.01;top+=1
assert expected['__worst_expense__'] in read(A/'insight.json')[0]['[Despesa]']
result={'status':'PASS','contas':len(actual),'contasNoRanking':top,'insightDespesa':'confere com o pior impacto independente do Excel'}
(A/'account-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result)
