"""Simplifica o modelo semântico sem alterar o relatório.

1. As nove consultas fLancamentoX_anoY deixam de ser carregadas: viram expressões
   (staging) em expressions.tmdl e continuam alimentando fLancamentos.
2. Remove Table_1…Table_8: ocultas, sem uso em visuais/medidas/relacionamentos e
   ligadas a um caminho absoluto do Excel original.
3. Remove os 27 relacionamentos das tabelas de origem e as referências em model.tmdl.

Uso único: aborta se as expressões já existirem. Faça backup antes (artifacts/simplificacao).
Arquivos gravados em UTF-8 sem BOM, preservando CRLF.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEF = ROOT / 'DRE Moderno.SemanticModel' / 'definition'
TABLES = DEF / 'tables'
STAGING = [f'fLancamento{i}_ano{j}' for j in (1, 2, 3) for i in (1, 2, 3)]
LEGACY = [f'Table_{n}' for n in range(1, 9)]
NL = '\r\n'


def read(path):
    return path.read_bytes().decode('utf-8').replace('\r\n', '\n')


def write(path, text):
    path.write_bytes(text.replace('\n', NL).encode('utf-8'))


def ensure_unused():
    """Garante que nenhuma tabela a remover é usada no relatório ou em DAX."""
    report = ROOT / 'DRE Moderno.Report' / 'definition'
    names = STAGING + LEGACY
    for file in report.rglob('*.json'):
        text = file.read_text(encoding='utf-8')
        for name in names:
            if f'"{name}"' in text:
                sys.exit(f'ABORTADO: {name} referenciada em {file}')
    for file in TABLES.glob('*.tmdl'):
        if file.stem in names:
            continue
        text = read(file)
        for name in names:
            # fLancamentos combina as origens em M: permitido. Proibido em DAX (Tabela[col] ou 'Tabela').
            if re.search(rf"(?<![\w']){name}\[|'{name}'", text):
                sys.exit(f'ABORTADO: {name} usada em DAX de {file.name}')


def staging_expression(name):
    text = read(TABLES / f'{name}.tmdl')
    tag = re.search(r'^\tlineageTag: (\S+)', text, re.M).group(1)
    body = re.search(r'^\t\tsource =\n(.*?)(?=\n\s*\n\tannotation|\Z)', text, re.S | re.M).group(1)
    lines = [line[2:] if line.startswith('\t\t\t\t') else line for line in body.rstrip().split('\n')]
    return (f'expression {name} =\n' + '\n'.join(lines) +
            f'\n\tlineageTag: {tag}\n\n\tannotation PBI_ResultType = Table\n\n')


def main():
    expressions = DEF / 'expressions.tmdl'
    current = read(expressions)
    if any(f'expression {name} ' in current for name in STAGING):
        sys.exit('ABORTADO: migração já aplicada.')
    ensure_unused()

    write(expressions, current.rstrip('\n') + '\n\n' + ''.join(staging_expression(n) for n in STAGING))

    relationships = DEF / 'relationships.tmdl'
    blocks = re.split(r'\n(?=relationship )', read(relationships).strip('\n'))
    kept = [b for b in blocks if not re.search(r'fromColumn: (fLancamento\d_ano\d|Table_\d)\.', b)]
    write(relationships, '\n\n'.join(b.strip('\n') for b in kept) + '\n\n')

    model = DEF / 'model.tmdl'
    text = read(model)
    for name in STAGING + LEGACY:
        text = text.replace(f'ref table {name}\n', '')
    text = re.sub(r',"Table_\d"', '', text)
    write(model, text)

    for name in STAGING + LEGACY:
        (TABLES / f'{name}.tmdl').unlink()

    print(f'OK: {len(STAGING)} consultas sem carga, {len(LEGACY)} tabelas legadas removidas, '
          f'{len(blocks) - len(kept)} relacionamentos removidos; {len(kept)} mantidos.')


if __name__ == '__main__':
    main()
