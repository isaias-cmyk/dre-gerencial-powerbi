"""Gera cópia tratada local; nunca altera o Excel de origem."""
import argparse
from collections import Counter
from datetime import datetime, date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
args = parser.parse_args()
original_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
book = openpyxl.load_workbook(args.source, read_only=True, data_only=True)
clean = {}
for sheet in book:
    iterator = sheet.iter_rows(values_only=True)
    headers = list(next(iterator))
    wanted = ['id','index','contaGerencial','subtotal','empresa'] if sheet.title == 'dEstruturaDRE' else [h for h in headers if h is not None]
    indices = [headers.index(h) for h in wanted]
    rows = []
    for raw in iterator:
        row = [raw[i] if i < len(raw) else None for i in indices]
        if not any(v is not None for v in row):
            continue
        if row[0] is None:
            raise ValueError('Linha sem chave: ' + sheet.title)
        for i, name in enumerate(wanted):
            if name in {'id','planoContas_id','mascaraDRE_id'}:
                if not isinstance(row[i], str):
                    raise ValueError('Código não textual na origem: ' + sheet.title)
                row[i] = row[i].strip()
            elif name == 'competencia_data':
                if not isinstance(row[i], (datetime,date)):
                    raise ValueError('Data inválida: ' + sheet.title)
            elif name in {'index','subtotal','detalharN2','tipoLancamento'}:
                if row[i] != int(row[i]):
                    raise ValueError('Inteiro inválido')
                row[i] = int(row[i])
        rows.append(row)
    if sheet.title.startswith('f'):
        key_index = wanted.index('planoContas_id')
        for row in rows:
            row.append(row[key_index].split('.')[0])
        wanted.append('filial_id')
    clean[sheet.title] = (wanted, rows)
book.close()

plan = clean['dPlanoConta'][1]
structure = clean['dEstruturaDRE'][1]
plan_keys = [r[0] for r in plan]
structure_keys = [r[0] for r in structure]
assert len(plan_keys) == len(set(plan_keys)), 'Plano duplicado'
assert len(structure_keys) == len(set(structure_keys)), 'Estrutura duplicada'
assert set(r[5] for r in plan) <= set(structure_keys), 'Máscaras órfãs'
branches = sorted(set((r[0].split('.')[0],r[4]) for r in structure))
assert len(branches) == len(set(r[0] for r in branches)), 'Filial ambígua'
clean['dFilial'] = (['id','Filial'],branches)
sources = sorted(n for n in clean if n.startswith('fLancamento'))
combined = [row for name in sources for row in clean[name][1]]
clean['fLancamentos'] = (clean[sources[0]][0],combined)

summary = {'source_sha256':original_hash,'sheets':{},'checks':{}}
for name,(headers,rows) in clean.items():
    info = {'rows':len(rows),'columns':headers}
    if name.startswith('f'):
        assert set(r[1] for r in rows) <= set(plan_keys), 'Contas órfãs em ' + name
        assert all(isinstance(r[2],(int,float)) for r in rows), 'Valor inválido'
        assert len({(r[0],r[1]) for r in rows}) == len(rows), 'Grão duplicado em ' + name
        info.update(min_date=min(r[0] for r in rows).isoformat(), max_date=max(r[0] for r in rows).isoformat(), total=str(sum(Decimal(str(r[2])) for r in rows)))
    summary['sheets'][name] = info
summary['checks'] = {'unique_dimensions':True,'orphan_keys':0,'duplicate_month_account':0,'consolidated_rows':len(combined)}
all_dates = [r[0] for n in ['fLancamentos','fOrcamento','fPrevisao'] for r in clean[n][1]]
summary['calendar'] = {'start':date(min(d.year for d in all_dates),1,1).isoformat(),'end':date(max(d.year for d in all_dates),12,31).isoformat()}
summary['expected_by_year'] = {}
for name in ['fLancamentos','fOrcamento','fPrevisao']:
    summary['expected_by_year'][name] = {str(y):{'rows':sum(r[0].year==y for r in clean[name][1]),'total':str(sum(Decimal(str(r[2])) for r in clean[name][1] if r[0].year==y))} for y in sorted({r[0].year for r in clean[name][1]})}

output = ROOT/'data/processed/BaseDados_Tratada.xlsx'
output.parent.mkdir(parents=True,exist_ok=True)
dest = openpyxl.Workbook(); dest.remove(dest.active)
for name,(headers,rows) in clean.items():
    sheet = dest.create_sheet(name); sheet.append(headers)
    for row in rows: sheet.append(row)
    sheet.freeze_panes='A2'; sheet.auto_filter.ref=sheet.dimensions
    for cell in sheet[1]:
        cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='17365D')
    for column in sheet.columns:
        name=column[0].value
        sheet.column_dimensions[column[0].column_letter].width=24 if name != 'contaGerencial' else 42
        for cell in column[1:]:
            if name in {'id','planoContas_id','mascaraDRE_id','filial_id'}:cell.number_format='@'
            elif name=='competencia_data':cell.number_format='dd/mm/yyyy'
            elif name=='valor':cell.number_format='#,##0.00'
dest.save(output)
assert hashlib.sha256(args.source.read_bytes()).hexdigest()==original_hash, 'Origem alterada'
(ROOT/'artifacts/modelagem').mkdir(parents=True,exist_ok=True)
(ROOT/'artifacts/modelagem/source-profile.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('Planilha tratada:',output)
print('Linhas consolidadas:',len(combined),'Calendário:',summary['calendar'])
print('PASS: chaves, grão mensal/conta, integridade referencial e preservação da origem.')
