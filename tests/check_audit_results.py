"""Verifica cobertura, casos-limite DAX e preservação dos objetos existentes."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'artifacts/auditoria'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
src=read(A/'cobertura-fontes.json')['tabelas'];live=read(A/'cobertura-modelo.json')
assert {(t['tabela'],m):n for t in src for m,n in t['meses'].items()}=={(t['[Tabela]'],t['[Competencia]']):t['[Linhas]'] for t in live}
edges=read(A/'edges-after.json');assert len(edges)==108
checks=0
for row in edges:
 for current,prior,ratio in [('Receita','ReceitaAnterior','YoYReceita'),('Resultado','ResultadoAnterior','YoYResultado'),('DRE','DREAnterior','AH')]:
  x,y,z=(row['['+n+']'] for n in (current,prior,ratio))
  if x is None or y is None or y==0:assert z is None,(row,ratio)
  else:assert abs(z-(x-y)/abs(y))<1e-10,(row,ratio)
  checks+=1
 for c in ['CorDesvio','CorLinha']:assert re.fullmatch('#[0-9A-Fa-f]{6}',row['['+c+']'])
# As análises já conciliadas de AV/detalhes e meses alternados não mudam.
for name in ['detail','selection']:
 assert read(A/(name+'-before.json'))==read(A/(name+'-after.json')),name
model=ROOT/'DRE Moderno.SemanticModel/definition'
assert (model/'relationships.tmdl').read_bytes()==(A/'model-before/relationships.tmdl').read_bytes()
before={p.stem for p in (A/'model-before/tables').glob('*.tmdl')}
assert before=={p.stem for p in (model/'tables').glob('*.tmdl')}
for name in before:
 old=(A/'model-before/tables'/f'{name}.tmdl').read_text(encoding='utf-8-sig')
 new=(model/'tables'/f'{name}.tmdl').read_text(encoding='utf-8-sig')
 assert old.split('\tpartition ',1)[1]==new.split('\tpartition ',1)[1],('Consulta alterada',name)
 assert re.findall(r'lineageTag: (.*)',old)==re.findall(r'lineageTag: (.*)',new)
 if name=='fLancamentos':
  for measure in ['Variação YoY %','Crescimento Receita %','DRE AH %']:
   pattern=r"(?m)^\tmeasure '"+re.escape(measure)+r"' = [^\r\n]*"
   old=re.sub(pattern,'<expressão auditada>',old);new=re.sub(pattern,'<expressão auditada>',new)
 assert old==new,('Mudança semântica fora das três medidas autorizadas',name)
pages=ROOT/'DRE Moderno.Report/definition/pages'
oldpaths={str(p.relative_to(A/'pages-before')) for p in (A/'pages-before').rglob('visual.json')}
newpaths={str(p.relative_to(pages)) for p in pages.rglob('visual.json')}
assert oldpaths==newpaths and len(newpaths)==71
meta=read(pages/'pages.json');beforemeta=read(A/'pages-before/pages.json')
assert meta['pageOrder']==beforemeta['pageOrder'] and meta['activePageName'] in meta['pageOrder']
for relative in newpaths:
 old=read(A/'pages-before'/relative);new=read(pages/relative)
 assert old['position']==new['position'] and old['name']==new['name']
 for role,value in old['visual'].get('query',{}).get('queryState',{}).items():
  assert [p['field'] for p in value['projections']]==[p['field'] for p in new['visual']['query']['queryState'][role]['projections']]
result={'status':'PASS','competencias':len(live),'casosDAX':checks,'linhasContexto':len(edges),'visuaisPreservados':len(newpaths),'tabelasPreservadas':len(before),'consultasM':'inalteradas','relacionamentos':'inalterados','AVDetalhada':'preservada','mesesAlternados':'preservados'}
(A/'resultado.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result)
