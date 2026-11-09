"""Baixa clientes oficiais Microsoft para validação local, sem instalação global."""
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

VERSION = '19.118.3'
ROOT = Path(__file__).resolve().parents[1]
destination = ROOT/'artifacts/tools/tom'
destination.mkdir(parents=True,exist_ok=True)
for package in ['microsoft.analysisservices','microsoft.analysisservices.adomdclient']:
    url=f'https://api.nuget.org/v3-flatcontainer/{package}/{VERSION}/{package}.{VERSION}.nupkg'
    with urlopen(url,timeout=60) as response:
        archive=ZipFile(BytesIO(response.read()))
    for name in archive.namelist():
        if name.startswith('lib/net8.0/') and name.count('/')==2 and name.endswith('.dll'):
            (destination/Path(name).name).write_bytes(archive.read(name))
    print(package,VERSION)
