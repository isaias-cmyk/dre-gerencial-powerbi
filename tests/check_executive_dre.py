"""Confere orçamento, AV, AH, YTD e ano completo das 13 linhas contra Excel."""
from pathlib import Path
from decimal import Decimal
import json,sys
R=Path(__file__).resolve().parents[1];A=R/'artifacts/executivo'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
modes=['Seleção','Acumulado no ano','Ano completo']
if '--prepare' in sys.argv:
 for i,mode in enumerate(modes):
  q='EVALUATE SUMMARIZECOLUMNS(dCalendario[Ano],dCalendario[MesNum],dFilial[id],dDRE[Ordem],TREATAS({"'+mode+'"},dPeriodo[Modo]),"Real",[DRE Realizado],"Orc",[DRE Orçamento Comparável],"AA",[DRE AA Comparável],"Impacto",[DRE Impacto Orçamentário R$],"Pct",[DRE Impacto Orçamentário %],"AV",[DRE AV %],"AH",[DRE AH Comparável %],"Contagem",1)'
  (A/f'dre-{i}.dax').write_text(q,encoding='utf-8')
 sys.exit()
ref=read(R/'artifacts/dre/reference.json');L={(r['cenario'],r['ano'],r['mes'],r['filial'],r['grupo']):Decimal(r['valor']) for r in ref}
groups={1:[1],2:[2],3:[1,2],4:[4],5:[1,2,4],6:[6],7:[7],8:[1,2,4,6,7],9:[9],10:[10],11:[1,2,4,6,7,9,10],12:[12],13:[1,2,4,6,7,9,10,12]}
def total(s,y,ms,b,gs):
 v=[L[(s,y,m,b,g)] for m in ms for g in gs if (s,y,m,b,g) in L];return sum(v,Decimal(0)) if v else None
def div(x,y):return None if x is None or y in (None,0) else x/y
n=0;lines=0
for i in range(3):
 rows=read(A/f'dre-{i}.json');assert len(rows)==1404
 for r in rows:
  y,m,b,g=(r[k] for k in ['dCalendario[Ano]','dCalendario[MesNum]','dFilial[id]','dDRE[Ordem]'])
  ms=[m] if i==0 else list(range(1,m+1)) if i==1 else list(range(1,13))
  available=[j for j in ms if ('Realizado',y,j,b,1) in L]
  x=total('Realizado',y,ms,b,groups[g]);o=total('Orcado',y,available,b,groups[g]);p=total('Realizado',y-1,available,b,groups[g]) if available and all(('Realizado',y-1,j,b,1) in L for j in available) else None
  impact=None if x is None or o is None else x-o
  expected={'Real':x,'Orc':o,'AA':p,'Impacto':impact,'Pct':div(impact,abs(o) if o is not None else None),'AV':div(x,total('Realizado',y,ms,b,[1,2])),'AH':div(None if x is None or p is None else x-p,abs(p) if p is not None else None)}
  for k,v in expected.items():
   actual=r['['+k+']'];assert (actual is None)==(v is None),(i,y,m,b,g,k,actual,v)
   if v is not None:assert abs(float(actual)-float(v))<(1e-8 if k in ['Pct','AV','AH'] else .01),(i,y,m,b,g,k,actual,v)
   n+=1
  lines+=1
result={'status':'PASS','contextosDRE':lines,'comparacoes':n,'modos':modes}
(A/'dre-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result)
