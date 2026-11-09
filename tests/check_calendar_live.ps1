param(
    [Parameter(Mandatory=$true)][int]$Port,
    [Parameter(Mandatory=$true)][string]$Database
)
# Somente leitura: o refresh deve ser concluído pela interface do Desktop.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
Get-ChildItem (Join-Path $root 'artifacts/tools/tom') -Filter '*.dll' |
    Where-Object Name -notlike '*resources*' | ForEach-Object {
        [System.Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null
    }
$expected = Get-Content (Join-Path $root 'artifacts/modelagem/source-profile.json') -Raw | ConvertFrom-Json
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port;Initial Catalog=$Database")
$results = [System.Collections.Generic.List[object]]::new()
function Read-Dax([string]$query) {
    $command = $connection.CreateCommand()
    $command.CommandText = $query
    $command.CommandTimeout = 60
    $reader = $command.ExecuteReader()
    $rows = [System.Collections.Generic.List[object]]::new()
    try {
        while ($reader.Read()) {
            $row = [ordered]@{}
            for ($i=0; $i -lt $reader.FieldCount; $i++) {
                $row[$reader.GetName($i)] = if ($reader.IsDBNull($i)) {$null} else {$reader.GetValue($i)}
            }
            $rows.Add([pscustomobject]$row)
        }
    } finally { $reader.Close(); $command.Dispose() }
    return $rows.ToArray()
}
try {
    $connection.Open()
    $calendar = @(Read-Dax @'
EVALUATE ROW("Dias", COUNTROWS(dCalendario),
 "Unicas", DISTINCTCOUNT(dCalendario[Data]),
 "Nulas", COUNTBLANK(dCalendario[Data]),
 "Inicio", FORMAT(MIN(dCalendario[Data]),"yyyy-MM-dd"),
 "Fim", FORMAT(MAX(dCalendario[Data]),"yyyy-MM-dd"))
'@)[0]
    $days = ([datetime]$expected.calendar.end - [datetime]$expected.calendar.start).Days + 1
    if ($calendar.'[Dias]' -ne $days -or $calendar.'[Unicas]' -ne $days -or $calendar.'[Nulas]' -gt 0 -or
        $calendar.'[Inicio]' -ne $expected.calendar.start -or $calendar.'[Fim]' -ne $expected.calendar.end) {
        throw 'Datas duplicadas, faltantes ou fora da faixa esperada'
    }
    $results.Add(@{test='Calendário contínuo, único e completo';result=$calendar})
    foreach ($table in @('fLancamentos','fOrcamento','fPrevisao')) {
        $query = 'EVALUATE SUMMARIZECOLUMNS(dCalendario[Ano], "Linhas", COUNTROWS('+$table+'), "Total", SUM('+$table+'[valor]))'
        $rows = @(Read-Dax $query)
        foreach ($row in $rows) {
            $year = [string]$row.'dCalendario[Ano]'
            $yearExpected = $expected.expected_by_year.$table.$year
            if ($null -eq $yearExpected -or $row.'[Linhas]' -ne $yearExpected.rows -or
                [Math]::Abs([double]$row.'[Total]' - [double]$yearExpected.total) -gt 0.01) {
                throw "Filtro por ano ou total divergente: $table / $year"
            }
        }
        $count = @($expected.expected_by_year.$table.PSObject.Properties).Count
        if ($rows.Count -ne $count) { throw "Quantidade de anos divergente em $table" }
        $results.Add(@{test="Filtro anual $table conciliado com Excel";result=$rows})
    }
    $month = @(Read-Dax @'
EVALUATE CALCULATETABLE(
 ROW("Realizado",COALESCE(COUNTROWS(fLancamentos),0),
 "Orcamento",COUNTROWS(fOrcamento),"Previsao",COUNTROWS(fPrevisao)),
 dCalendario[AnoMesINT]=202312)
'@)[0]
    if ($month.'[Realizado]' -ne 0 -or $month.'[Orcamento]' -ne 129 -or $month.'[Previsao]' -ne 129) {
        throw 'Filtro de dezembro/2023 falhou'
    }
    $results.Add(@{test='Mês futuro mantém orçamento/previsão e não inventa realizado';result=$month})
    $branches = @(Read-Dax @'
EVALUATE SUMMARIZECOLUMNS(dFilial[id], dCalendario[Ano], "Linhas", COUNTROWS(fLancamentos))
'@)
    if ($branches.Count -ne 9) { throw 'Filiais/anos inesperados' }
    foreach ($row in $branches) {
        $count = if ($row.'dCalendario[Ano]' -eq 2023) {215} else {516}
        if ($row.'[Linhas]' -ne $count) { throw 'Filtro combinado filial/ano falhou' }
    }
    $results.Add(@{test='Filtro combinado filial/ano';result=$branches})
    $output = Join-Path $root 'artifacts/modelagem/calendar-live-results.json'
    $results | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $output -Encoding utf8
    'PASS: calendário, totais por ano das três fatos, dezembro futuro e filtro filial/ano.'
} finally { $connection.Close(); $connection.Dispose() }
