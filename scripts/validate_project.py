"""Validação estática; não substitui o Power BI Desktop."""
import json
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen
from jsonschema import validators
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=128)
def retrieve(uri):
    u = urlparse(uri)
    if u.scheme != 'https' or u.hostname not in {'developer.microsoft.com', 'raw.githubusercontent.com'}:
        raise ValueError('Host de schema não autorizado: ' + uri)
    if u.hostname == 'raw.githubusercontent.com' and not u.path.startswith('/microsoft/'):
        raise ValueError('Repositório não autorizado: ' + uri)
    with urlopen(uri, timeout=30) as response:
        return Resource.from_contents(json.load(response))

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def contained(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.exists():
        raise ValueError('Referência ausente ou fora do workspace')
    return path

def main():
    failures = 0
    registry = Registry(retrieve=retrieve)
    projects = sorted(ROOT.glob('*.pbip'))
    if not projects:
        print('FAIL: nenhum PBIP'); return 1
    files = set(projects)
    for folder in list(ROOT.glob('*.Report')) + list(ROOT.glob('*.SemanticModel')):
        files.update(p for p in folder.rglob('*') if p.is_file() and
                     (p.suffix in {'.json', '.pbir', '.pbism'} or p.name == '.platform'))
    for path in sorted(files):
        label = path.relative_to(ROOT)
        try:
            data = read(path)
            uri = data.get('$schema') if isinstance(data, dict) else None
            if uri:
                schema = retrieve(uri).contents
                cls = validators.validator_for(schema)
                cls.check_schema(schema)
                cls(schema, registry=registry).validate(data)
                print('PASS schema:', label)
            else:
                print('JSON OK; sem schema declarado:', label)
        except Exception as exc:
            failures += 1
            # Evitar imprimir valores de instâncias que possam conter segredos.
            print('FAIL:', label, type(exc).__name__)
    try:
        for pbip in projects:
            for artifact in read(pbip)['artifacts']:
                report = contained(ROOT, artifact['report']['path'])
                descriptor = read(report / 'definition.pbir')
                model = contained(report, descriptor['datasetReference']['byPath']['path'])
                for required in ['definition.pbism', 'definition/database.tmdl', 'definition/model.tmdl']:
                    contained(model, required)
                pages = report / 'definition/pages'
                metadata = read(pages / 'pages.json')
                order = metadata['pageOrder']
                assert len(order) == len(set(order)), 'IDs duplicados'
                assert metadata.get('activePageName') in order, 'Página ativa ausente'
                assert set(order) == {p.parent.name for p in pages.glob('*/page.json')}, 'Ordem divergente'
                for page_id in order:
                    assert read(contained(pages, page_id + '/page.json'))['name'] == page_id
        print('PASS: referências estruturais PBIP/PBIR e presença TMDL')
    except Exception as exc:
        failures += 1
        print('FAIL referências:', type(exc).__name__)
    print('PENDENTE: desserialização TMDL, DAX/M e validação funcional no Desktop.')
    return 1 if failures else 0

if __name__ == '__main__':
    sys.exit(main())
