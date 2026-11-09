param([Parameter(Mandatory)][int]$Port,[Parameter(Mandatory)][string]$Database,[Parameter(Mandatory)][string]$QueryFile,[Parameter(Mandatory)][string]$OutputFile)
# Consultas EVALUATE somente de leitura; nunca processa o modelo embarcado.
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
$query=Get-Content -LiteralPath $QueryFile -Raw
if($query -notmatch '^\s*(DEFINE\s|EVALUATE\s)'){throw 'Somente consultas DAX de leitura'}
Get-ChildItem "$root/artifacts/tools/tom" -Filter '*.dll' | Where-Object Name -notlike '*resources*' | ForEach-Object {[System.Reflection.Assembly]::LoadFrom($_.FullName)|Out-Null}
$c=[Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=localhost:$Port;Initial Catalog=$Database")
try{
 $c.Open();$cmd=$c.CreateCommand();$cmd.CommandText=$query;$cmd.CommandTimeout=120
 $r=$cmd.ExecuteReader();$rows=[System.Collections.Generic.List[object]]::new()
 while($r.Read()){$v=[ordered]@{};for($i=0;$i -lt $r.FieldCount;$i++){$v[$r.GetName($i)]=if($r.IsDBNull($i)){$null}else{$r.GetValue($i)}};$rows.Add($v)}
 $r.Close();$cmd.Dispose()
 ConvertTo-Json -InputObject $rows.ToArray() -Depth 12 | Set-Content -LiteralPath $OutputFile -Encoding utf8
 "READ: $($rows.Count) linhas; $OutputFile"
}finally{$c.Close();$c.Dispose()}
