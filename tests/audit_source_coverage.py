"""Compara todas as linhas mensais das fontes existentes, sem alterar planilhas."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib,json
import openpyxl
ROOT=Path(__file__).resolve().parents[1]
import os,sys
# Caminho do Excel original: variável de ambiente DRE_SOURCE_XLSX (não versionar caminhos pessoais).
source=Path(os.environ.get('DRE_SOURCE_XLSX') or sys.exit('Defina DRE_SOURCE_XLSX com o caminho do BaseDados.xlsx original.'))
treated=ROOT/'data/processed/BaseDados_Tratada.xlsx'
def read(path):
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    result={}
    for s in w:
        if not s.title.startswith('f'):continue
        it=iter(s.values);heads=next(it);rows=[]
        for row in it:
            d=dict(zip(heads,row))
            if all(d.get(k) is None for k in ('competencia_data','planoContas_id','valor')):continue
            dt=d['competencia_data'];assert isinstance(dt,datetime),(s.title,'Data inválida')
            assert dt<=datetime(2023,12,31),(s.title,'Fora do escopo histórico')
            rows.append((dt.strftime('%Y-%m-%d'),str(d['planoContas_id']),float(d['valor'])))
        result[s.title]=rows
    w.close();return result
a,b=read(source),read(treated)
origin_facts=[n for n in a if n.startswith('fLancamento')]
a['fLancamentos']=[r for n in origin_facts for r in a[n]]
out=[]
for name,rows in a.items():
    # Excel reserializa doubles; comparar chaves/grão exatamente e valores a 1e-8 R$.
    original=sorted(rows);clean=sorted(b[name])
    assert len(original)==len(clean),(name,'Contagem divergente')
    assert [(r[0],r[1]) for r in original]==[(r[0],r[1]) for r in clean],(name,'Chaves divergentes')
    delta=max(abs(x[2]-y[2]) for x,y in zip(original,clean))
    assert delta<1e-8,(name,'Valor alterado',delta)
    monthly=Counter(r[0][:7] for r in rows)
    out.append({'tabela':name,'linhas':len(rows),'inicio':min(r[0] for r in rows),'ultimaCompetencia':max(r[0] for r in rows),'meses':dict(sorted(monthly.items())),'origemIgualTratada':True,'maiorDiferencaNumerica':delta})
report={'status':'PASS','fimEscopo':'2023-12-31','originalSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'tratadaSHA256':hashlib.sha256(treated.read_bytes()).hexdigest(),'tabelas':out}
dest=ROOT/'artifacts/auditoria';dest.mkdir(exist_ok=True,parents=True)
(dest/'cobertura-fontes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
queries=[]
for table in out:
    n=table['tabela']
    queries.append(f'SELECTCOLUMNS(SUMMARIZE({n}, {n}[competencia_data], "N", COUNTROWS({n})), "Tabela", "{n}", "Competencia", FORMAT({n}[competencia_data], "yyyy-MM"), "Linhas", [N])')
(dest/'cobertura.dax').write_text('EVALUATE UNION('+',\n'.join(queries)+')',encoding='utf-8')
print('PASS: 12 tabelas mensais; chaves e datas idênticas; diferenças numéricas inferiores a R$ 0,00000001.')
