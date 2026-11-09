# Validação

Executar na raiz:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r tests/requirements.txt
.\.venv\Scripts\python.exe scripts/validate_project.py
```

O script verifica JSON, schemas declarados de hosts oficiais Microsoft, caminhos PBIP → Report → SemanticModel e ordem/IDs das páginas. Não modifica artefatos. Código de saída diferente de zero indica falha. JSON sem schema é explicitamente reportado. Precisa de rede para schemas e referências remotas.

Validação atual: executar também `scripts/validate_tmdl.ps1`, `tests/check_calendar_live.ps1`, `tests/check_dre_live.ps1` e `tests/check_measures_live.ps1` (todas as medidas no total/ano/filial). Os scripts .ps1 carregam bibliotecas .NET 8: usar **PowerShell 7** (`pwsh -File ...`); no Windows PowerShell 5.1 o `TmdlSerializer` não é encontrado. Testes que releem o Excel original exigem a variável de ambiente `DRE_SOURCE_XLSX` com o caminho do arquivo. Os dois últimos recebem `-Port` e `-Database` da instância atual do Desktop; descobrir esses valores a cada sessão, nunca reutilizar sem conferir. As consultas são somente de leitura. Atualizações de dados devem ocorrer pela interface do Desktop.

Para auditar cobertura antes de editar, executar `tests/audit_source_coverage.py` com Python/openpyxl. Esse teste lê a origem existente e a cópia tratada, gera `artifacts/auditoria/cobertura-fontes.json` e `cobertura.dax`. Consultar esse DAX com `scripts/read_dax.ps1 -Port <porta> -Database <id> -QueryFile artifacts/auditoria/cobertura.dax -OutputFile artifacts/auditoria/cobertura-modelo.json`.

Os casos DAX adicionais estão em `tests/audit_dax_edges.dax`; consultar com o mesmo script, usando saída `artifacts/auditoria/edges-after.json`. `tests/check_audit_results.py` exige os snapshots antes/depois e saídas locais da auditoria descritos em docs/auditoria-dax-cobertura.md. Não usar a ausência desses artefatos ignorados como aprovação. Resultados numéricos não substituem a inspeção da renderização no Desktop.
