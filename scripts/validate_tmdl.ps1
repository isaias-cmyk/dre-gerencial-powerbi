$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
$library = Join-Path $root 'artifacts/tools/tom'
Get-ChildItem $library -Filter 'Microsoft.AnalysisServices*.dll' |
    Where-Object Name -notlike '*resources*' | ForEach-Object {
        [System.Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null
    }
$database = [Microsoft.AnalysisServices.Tabular.TmdlSerializer]::DeserializeDatabaseFromFolder(
    (Join-Path $root 'DRE Moderno.SemanticModel/definition'))
$model = $database.Model
$calendar = $model.Tables.Find('dCalendario')
if ($calendar.DataCategory -ne 'Time' -or -not $calendar.Columns.Find('Data').IsKey) {
    throw 'Calendário não marcado com Data como chave'
}
foreach ($table in $model.Tables) {
    if ($table.Name -like 'f*') {
        $dateRelationships = @($model.Relationships | Where-Object {
            $_.FromTable.Name -eq $table.Name -and $_.ToTable.Name -eq 'dCalendario' -and $_.IsActive
        })
        if ($dateRelationships.Count -ne 1) { throw "Calendário inválido em $($table.Name)" }
    }
}
foreach ($relationship in $model.Relationships) {
    if ($relationship.CrossFilteringBehavior.ToString() -ne 'OneDirection') {
        throw 'Relacionamento bidirecional inesperado'
    }
    if ($relationship.ToCardinality.ToString() -ne 'One') { throw 'Lado dimensão não é 1' }
    if ($relationship.FromColumn.DataType -ne $relationship.ToColumn.DataType) {
        throw 'Tipos incompatíveis no relacionamento'
    }
}
"PASS TOM: $($model.Tables.Count) tabelas; $($model.Relationships.Count) relações; calendário e tipos coerentes."
