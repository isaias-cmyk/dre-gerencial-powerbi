"""Referências reais, limites de layout e preservação de páginas/IDs PBIR."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];P=R/'DRE Moderno.Report/definition/pages';A=R/'artifacts/executivo'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def nodes(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from nodes(v)
 elif isinstance(x,list):
  for v in x:yield from nodes(v)
old=A/'pages-before';assert read(old/'pages.json')['pageOrder']==read(P/'pages.json')['pageOrder']
before={str(p.relative_to(old)) for p in old.rglob('visual.json')};after={str(p.relative_to(P)) for p in P.rglob('visual.json')};assert before<=after and len(before)==71 and len(after)==86
bindings=0
for f in P.rglob('visual.json'):
 d=read(f);page=read(f.parents[2]/'page.json');pos=d['position']
 assert d['name']==f.parent.name
 assert pos['x']>=0 and pos['y']>=0 and pos['x']+pos['width']<=page['width'] and pos['y']+pos['height']<=page['height'],str(f)
 aliases={s['Name']:s['Entity'] for node in nodes(d) for s in node.get('From',[])}
 for node in nodes(d):
  for kind in ['Measure','Column']:
   v=node.get(kind)
   if not isinstance(v,dict) or 'Property' not in v:continue
   src=v['Expression']['SourceRef'];t=src.get('Entity') or aliases[src['Source']];n=v['Property']
   model=(R/'DRE Moderno.SemanticModel/definition/tables'/f'{t}.tmdl').read_text(encoding='utf-8-sig')
   assert re.search(r'\t'+kind.lower()+r" (?:'"+re.escape(n)+r"'|"+re.escape(n)+r")(?:\s|$)",model),(str(f),t,n)
   bindings+=1
result={'status':'PASS','paginas':5,'visuais':86,'idsAnterioresPreservados':71,'referenciasVerificadas':bindings,'limitesDoCanvas':'PASS'}
(A/'report-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result)
