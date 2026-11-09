param([int]$Port,[string]$Database)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
Get-ChildItem "$root/artifacts/tools/tom" -Filter '*.dll' | Where-Object Name -notlike '*resources*' | ForEach-Object { [System.Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null }
$c=[Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=localhost:$Port;Initial Catalog=$Database")
$results=[System.Collections.Generic.List[object]]::new()
try {
 $c.Open()
 foreach($scenario in @('Realizado','Previsto','Orcado')) {
  $measure=if($scenario -eq 'Orcado'){'Valor Orçado'}else{'Valor '+$scenario}
  $cmd=$c.CreateCommand()
  $cmd.CommandText="EVALUATE SUMMARIZECOLUMNS(dCalendario[Ano],dCalendario[MesNum],dFilial[id],dPlanoConta[GrupoDRE],`"Valor`",[$measure])"
  $r=$cmd.ExecuteReader()
  while($r.Read()) { $results.Add(@{cenario=$scenario;ano=$r.GetValue(0);mes=$r.GetValue(1);filial=$r.GetValue(2);grupo=$r.GetValue(3);valor=$r.GetValue(4)}) }
  $r.Close();$cmd.Dispose()
 }
 $expected=Get-Content "$root/artifacts/dre/reference.json" -Raw | ConvertFrom-Json
 $lookup=@{}
 foreach($row in $expected){$lookup["$($row.cenario)|$($row.ano)|$($row.mes)|$($row.filial)|$($row.grupo)"]=[decimal]$row.valor}
 if($results.Count -ne $lookup.Count){throw "Contagem divergente: $($results.Count) vs $($lookup.Count)"}
 $maxDelta=[decimal]0
 foreach($row in $results){
  $key="$($row.cenario)|$($row.ano)|$($row.mes)|$($row.filial)|$($row.grupo)"
  if(-not $lookup.ContainsKey($key)){throw "Chave inesperada: $key"}
  $delta=[Math]::Abs([decimal]$row.valor-$lookup[$key])
  $maxDelta=[Math]::Max($maxDelta,$delta)
  if($delta -gt 0.01){throw "Divergência contábil: $key / $delta"}
 }
 $groups=@{1=@(1);2=@(2);3=@(1,2);4=@(4);5=@(1,2,4);6=@(6);7=@(7);8=@(1,2,4,6,7);9=@(9);10=@(10);11=@(1,2,4,6,7,9,10);12=@(12);13=@(1,2,4,6,7,9,10,12)}
 $lineCount=0
 foreach($scenario in @('Realizado','Previsto')) {
  $cmd=$c.CreateCommand()
  $cmd.CommandText="EVALUATE SUMMARIZECOLUMNS(dCalendario[Ano],dCalendario[MesNum],dFilial[id],dDRE[Ordem],`"Valor`",[DRE $scenario])"
  $r=$cmd.ExecuteReader()
  while($r.Read()) {
   $yr=$r.GetValue(0);$mo=$r.GetValue(1);$branch=$r.GetValue(2);$line=[int]$r.GetValue(3)
   $sum=[decimal]0
   foreach($group in $groups[$line]){$sum+=$lookup["$scenario|$yr|$mo|$branch|$group"]}
   if([Math]::Abs([decimal]$r.GetValue(4)-$sum) -gt 0.01){throw "Subtotal DRE divergente: $scenario/$yr/$mo/$branch/$line"}
   $lineCount++
  }
  $r.Close();$cmd.Dispose()
 }
 if($lineCount -ne 2535){throw "Cobertura DRE inesperada: $lineCount"}
 $cmd=$c.CreateCommand()
 $cmd.CommandText=@'
EVALUATE ROW(
 "AV", CALCULATE([DRE AV %],dDRE[Ordem]=3,dCalendario[Ano]=2022),
 "YTD", CALCULATE([DRE Realizado],dDRE[Ordem]=13,dCalendario[AnoMesINT]=202205,dPeriodo[Modo]="Acumulado no ano"),
 "YTDReferencia", CALCULATE([Resultado Líquido],dCalendario[Ano]=2022,dCalendario[MesNum]<=5),
 "AnoCompleto", CALCULATE([DRE Realizado],dDRE[Ordem]=13,dCalendario[AnoMesINT]=202205,dPeriodo[Modo]="Ano completo"),
 "AnoReferencia", CALCULATE([Resultado Líquido],dCalendario[Ano]=2022),
 "SemBaseAnterior", CALCULATE([DRE AH %],dDRE[Ordem]=13,dCalendario[Ano]=2021),
 "SemRealizado", CALCULATE([DRE Desvio R$],dDRE[Ordem]=13,dCalendario[AnoMesINT]=202312))
'@
 $r=$cmd.ExecuteReader();$null=$r.Read()
 if([Math]::Abs([double]$r.GetValue(0)-1) -gt 0.000001){throw 'AV receita líquida diferente de 100%'}
 if([Math]::Abs([double]$r.GetValue(1)-[double]$r.GetValue(2)) -gt 0.01){throw 'YTD divergente'}
 if([Math]::Abs([double]$r.GetValue(3)-[double]$r.GetValue(4)) -gt 0.01){throw 'Ano completo divergente'}
 if(-not $r.IsDBNull(5) -or -not $r.IsDBNull(6)){throw 'Brancos de comparabilidade incorretos'}
 $r.Close();$cmd.Dispose()
 @{status='PASS';comparacoes=$results.Count;linhasDRE=$lineCount;maiorDiferenca=$maxDelta;escopo='Grupos e 13 linhas DRE por mês/ano/filial; referência independente do Excel original'} | ConvertTo-Json | Set-Content "$root/artifacts/dre/reconciliation.json" -Encoding utf8
 "PASS: $($results.Count) agregações conciliadas; maior diferença $maxDelta"
} finally {$c.Close();$c.Dispose()}
