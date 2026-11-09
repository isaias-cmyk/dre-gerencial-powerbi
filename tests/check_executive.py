"""Referência decimal independente × DAX executado no Desktop (prepare/check)."""
from pathlib import Path
from decimal import Decimal
import json,sys,re
R=Path(__file__).resolve().parents[1]; A=R/'artifacts/executivo'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
groups={'Receita Líquida':[1,2],'Lucro Bruto':[1,2,4],'Resultado Operacional':[1,2,4,6,9],'Resultado Líquido':[1,2,4,6,7,9,10,12]}
fields={}
for n in groups:
 for suffix in ['', ' Orçamento Comparável',' AA Comparável',' Δ AA',' Δ Orçamento']: fields[n+suffix]=n+suffix
for n in ['Margem Bruta','Margem Líquida']:
 for suffix in [' %',' AA Comparável',' Orçamento Comparável',' Δ AA p.p.',' Δ Orçamento p.p.']: fields[n+suffix]=n+suffix
fields.update({'Meses':'Meses Realizados no Contexto','Waterfall':'SUMX(VALUES(dDRE[Ordem]),[Componente Waterfall DRE])','Insight':'Síntese Executiva'})
cases=[(y,m,b) for y in range(2021,2024) for m in range(13) for b in ['01','02','03','ALL']]
if '--prepare' in sys.argv:
 for monthly in [False,True]:
  for branch in [False,True]:
   pairs=', '.join('"'+a+'",'+('['+v+']' if a!='Waterfall' else v) for a,v in fields.items())
   cols='dCalendario[Ano],'+('dCalendario[MesNum],' if monthly else '')+('dFilial[id],' if branch else '')
   meta='"TestAno",SELECTEDVALUE(dCalendario[Ano]),"Mes",'+('SELECTEDVALUE(dCalendario[MesNum])' if monthly else '0')+',"Filial",'+('SELECTEDVALUE(dFilial[id])' if branch else '"ALL"')
   (A/f'executive-{int(monthly)}{int(branch)}.dax').write_text('EVALUATE SUMMARIZECOLUMNS('+cols+meta+','+pairs+')',encoding='utf-8')
 print('Preparados',len(cases),'contextos');sys.exit()
ref=read(R/'artifacts/dre/reference.json');lookup={(r['cenario'],r['ano'],r['mes'],r['filial'],r['grupo']):Decimal(r['valor']) for r in ref}
actual={(r['ano'],r['mes'],r['filial']) for r in ref if r['cenario']=='Realizado'}
def total(s,y,months,branches,gs):
 vals=[lookup[(s,y,m,b,g)] for m in months for b in branches for g in gs if (s,y,m,b,g) in lookup]
 return sum(vals,Decimal(0)) if vals else None
checks=0;maximum=0
def eq(value,want,tol=0.01):
 global checks,maximum
 checks+=1
 if want is None: assert value is None,('Esperado branco',value);return
 assert value is not None,('Valor ausente',want)
 diff=abs(float(value)-float(want));maximum=max(maximum,diff)
 assert diff<tol,(value,str(want),diff)
def div(x,y):return None if x is None or y in (None,0) else x/y
def sub(x,y):return None if x is None or y is None else x-y
data=[r for i in ['00','01','10','11'] for r in read(A/f'executive-{i}.json')];assert len(data)==len(cases)
for row in data:
 y,m,b=(row['['+k+']'] for k in ['TestAno','Mes','Filial']);bs=['01','02','03'] if b=='ALL' else [b];ms=list(range(1,13)) if m==0 else [m]
 available=[v for v in ms if any((y,v,z) in actual for z in bs)]
 prior=bool(available) and all((y-1,v,z) in actual for v in available for z in bs)
 expected={}
 for n,gs in groups.items():
  x=total('Realizado',y,ms,bs,gs);o=total('Orcado',y,available,bs,gs);p=total('Realizado',y-1,available,bs,gs) if prior else None
  expected.update({n:x,n+' Orçamento Comparável':o,n+' AA Comparável':p,n+' Δ AA':sub(x,p),n+' Δ Orçamento':sub(x,o)})
 for n,num in [('Margem Bruta','Lucro Bruto'),('Margem Líquida','Resultado Líquido')]:
  for suffix,target in [('', ' %'),(' AA Comparável',' AA Comparável'),(' Orçamento Comparável',' Orçamento Comparável')]:expected[n+target]=div(expected[num+suffix],expected['Receita Líquida'+suffix])
  for suffix in ['AA','Orçamento']:
   d=sub(expected[n+' %'],expected[n+' '+suffix+' Comparável']);expected[n+' Δ '+suffix+' p.p.']=None if d is None else d*100
 for name,want in expected.items():eq(row['['+name+']'],want,1e-8 if 'Margem' in name else .01)
 eq(row['[Meses]'],len(available) if available else None)
 eq(row['[Waterfall]'],expected['Resultado Líquido'])
 assert isinstance(row['[Insight]'],str)
 if not available: assert 'indisponível' in row['[Insight]'] and 'sem realizado' in row['[Insight]']
# Preservação física: todas as expressões anteriores, consultas e relações.
before=A/'model-before';after=R/'DRE Moderno.SemanticModel/definition'
assert (before/'relationships.tmdl').read_bytes()==(after/'relationships.tmdl').read_bytes()
count=0
for p in (before/'tables').glob('*.tmdl'):
 old=p.read_text(encoding='utf-8-sig');new=(after/'tables'/p.name).read_text(encoding='utf-8-sig')
 assert old.split('\tpartition ',1)[-1]==new.split('\tpartition ',1)[-1],p.name
 for block in re.findall(r'(?ms)^\tmeasure .*?(?=^\t(?:measure|column|partition) |\Z)',old):
  assert block.strip() in new,(p.name,block.splitlines()[0]);count+=1
result={'status':'PASS','contextos':len(data),'comparacoesNumericas':checks,'maiorDiferenca':maximum,'medidasAnterioresPreservadas':count,'consultasERelacionamentos':'inalterados','waterfall':'total igual ao resultado líquido; sem duplicar subtotais'}
(A/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
