param([int]$Port,[string]$Database)
# Regressão: todas as medidas do modelo avaliam sem erro no total, por ano e por filial.
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
Get-ChildItem "$root/artifacts/tools/tom" -Filter '*.dll' | ? Name -notlike '*resources*' | % { [Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null }
$c=[Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=localhost:$Port;Initial Catalog=$Database")
$c.Open()
$cmd=$c.CreateCommand(); $cmd.CommandText='SELECT [Name] FROM $SYSTEM.TMSCHEMA_MEASURES'
$r=$cmd.ExecuteReader(); $names=@(); while($r.Read()){ $names+=$r.GetString(0) }; $r.Close()
$fail=@(); $cells=0
foreach($n in $names){
  $m="[" + $n.Replace(']',']]') + "]"
  foreach($q in @("EVALUATE ROW(`"v`",$m)",
                  "EVALUATE SUMMARIZECOLUMNS(dCalendario[Ano],`"v`",$m)",
                  "EVALUATE SUMMARIZECOLUMNS(dFilial[Filial],`"v`",$m)")){
    try { $k=$c.CreateCommand(); $k.CommandText=$q; $rd=$k.ExecuteReader(); while($rd.Read()){ $cells++ }; $rd.Close() }
    catch { $fail+="$n :: $($_.Exception.InnerException.Message ?? $_.Exception.Message)" }
  }
}
$c.Close()
if($fail.Count){ $fail | Select -First 20; throw "FAIL: $($fail.Count) consultas de medida com erro" }
"PASS: $($names.Count) medidas avaliadas sem erro em total/ano/filial ($cells linhas)."
