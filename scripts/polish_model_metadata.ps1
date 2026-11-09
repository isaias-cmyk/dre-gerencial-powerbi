<#
.SYNOPSIS
  Organiza metadados do modelo para leitura (portfólio), sem alterar visuais nem resultados.
.DESCRIPTION
  Aplica via TOM na instância aberta do Power BI Desktop (operações de metadados suportadas
  para ferramentas externas: descrição, pasta, ocultar, expressão de medida). Depois, salvar no Desktop.
  - 49 medidas sem uso no relatório -> pasta "_Legado", ocultas (não excluídas).
  - Descrições nas medidas principais.
  - Colunas técnicas (chaves, sinal, máscara, auxiliares) ocultas.
  - 'Contexto Executivo': faixa de anos calculada em vez de "2021–2023" fixo.
  Uso: pwsh -File scripts/polish_model_metadata.ps1 -Port <porta> -Database <id> [-WhatIf]
#>
param([Parameter(Mandatory)][int]$Port,[Parameter(Mandatory)][string]$Database,[switch]$WhatIf)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot
Get-ChildItem "$root/artifacts/tools/tom" -Filter 'Microsoft.AnalysisServices*.dll' | ? Name -notlike '*resources*' | % { [Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null }
$server=[Microsoft.AnalysisServices.Tabular.Server]::new(); $server.Connect("Data Source=localhost:$Port")
$model=$server.Databases.GetByName($Database).Model
if(-not $model){ $model=$server.Databases.Find($Database).Model }
$f=$model.Tables['fLancamentos']

$legado=@('Registros Realizados','Receita Bruta Prevista','Receita Bruta Orçada','Deduções Prevista','Deduções Orçada','Custos Prevista','Custos Orçada','Lucro Bruto Prevista','Lucro Bruto Orçada','Despesas Operacionais Orçada','Resultado Financeiro Prevista','Resultado Financeiro Orçada','Depreciação e Amortização','Depreciação e Amortização Prevista','Depreciação e Amortização Orçada','Outras Receitas e Despesas','Outras Receitas e Despesas Prevista','Outras Receitas e Despesas Orçada','Resultado Operacional Prevista','Resultado Operacional Orçada','Resultado Antes dos Tributos','Resultado Antes dos Tributos Prevista','Resultado Antes dos Tributos Orçada','Tributos sobre Resultado','Tributos sobre Resultado Prevista','Tributos sobre Resultado Orçada','Margem Operacional %','Receita MTD','Resultado MTD','Realizado YTD','Previsto YTD','Resultado Ano Anterior','Variação YoY %','Receita Ano Anterior','Crescimento Receita %','Desvio Receita R$','Desvio Despesas R$','Atingimento do Orçamento %','Desvio Realizado x Previsto','Desvio %','DRE Base Previsto','DRE Previsto','DRE Desvio R$','DRE Desvio %','DRE Ano Anterior','DRE AH %','DRE Cor Desvio','DRE Peso Linha','DRE Situação')

$desc=[ordered]@{
 'Valor Realizado'='Realizado com sinal contábil: SUMX(valor × dPlanoConta[tipoLancamento]). Receitas positivas, custos e despesas negativos. Base de todas as medidas de realizado.'
 'Valor Orçado'='Orçamento com o mesmo sinal contábil do realizado (valor × tipoLancamento).'
 'Valor Previsto'='Previsão (forecast) com o mesmo sinal contábil do realizado (valor × tipoLancamento).'
 'Receita Bruta'='Realizado do grupo DRE 1 (receita operacional bruta).'
 'Deduções'='Realizado do grupo DRE 2 (deduções da receita); valor negativo.'
 'Receita Líquida'='Receita bruta + deduções (grupos DRE 1 e 2).'
 'Custos'='Realizado do grupo DRE 4 (custos de mercadorias e serviços); valor negativo.'
 'Lucro Bruto'='Receita líquida + custos (grupos DRE 1, 2 e 4).'
 'Despesas Operacionais'='Realizado do grupo DRE 6 (despesas operacionais); valor negativo.'
 'Resultado Financeiro'='Realizado do grupo DRE 7 (receitas menos despesas financeiras).'
 'Resultado Operacional'='Grupos DRE 1, 2, 4, 6 e 9: lucro bruto, despesas operacionais e depreciação. Exclui financeiro e outras receitas/despesas.'
 'Resultado Líquido'='Linha 13 da DRE: soma dos grupos 1, 2, 4, 6, 7, 9, 10 e 12.'
 'Margem Bruta %'='Lucro bruto ÷ receita líquida. Branco quando não há receita.'
 'Margem Líquida %'='Resultado líquido ÷ receita líquida. Branco quando não há receita.'
 'Participação Receita Filial %'='Receita líquida da filial ÷ receita líquida de todas as filiais selecionadas.'
 'Orçamento Comparável'='Orçamento restrito às competências que têm realizado no contexto (o realizado termina em mai/2023). Evita comparar meses realizados com o ano orçado inteiro.'
 'Impacto Orçamentário R$'='Realizado − orçamento comparável, ambos com sinal. Positivo = favorável (mais receita ou menos gasto).'
 'Comparação AA Disponível'='1 quando há um único ano selecionado e todos os seus meses com realizado existem no ano anterior; senão 0. Controla as comparações com o ano anterior.'
 'Receita Líquida AA Comparável'='Receita líquida dos mesmos meses do ano anterior (deslocamento de 12 meses das competências realizadas). Branco sem base comparável.'
 'Resultado Líquido AA Comparável'='Resultado líquido dos mesmos meses do ano anterior. Branco sem base comparável.'
 'DRE Base Realizado'='Valor de cada uma das 13 linhas de dDRE pela composição de grupos (ex.: linha 5 = grupos 1, 2 e 4). Subtotais ficam em branco no detalhamento por conta.'
 'DRE Realizado'='DRE Base Realizado no modo escolhido em dPeriodo: Seleção, Acumulado no ano (YTD) ou Ano completo.'
 'DRE Orçamento Comparável'='Linha da DRE no orçamento comparável, no mesmo modo de período da DRE Realizado.'
 'DRE AV %'='Análise vertical: linha da DRE ÷ receita líquida (linha 3) do mesmo contexto.'
 'DRE AH Comparável %'='Análise horizontal: variação contra os mesmos meses do ano anterior, dividida pelo módulo da base. Branco sem base (nunca −100%).'
 'Componente Waterfall DRE'='Linhas 3, 4, 6, 7, 9, 10 e 12 para a cascata; o total da cascata é igual ao resultado líquido.'
 'Top 8 Impacto Conta'='Impacto orçamentário das 8 contas (descricaoN2) com maior impacto absoluto no contexto.'
 'Contexto Executivo'='Texto do cabeçalho: ano ou faixa de anos, filial e quantidade de meses com realizado.'
}

$hide=@{
 'fLancamentos'=@('competencia_data','planoContas_id','filial_id','valor')
 'fOrcamento'=@('competencia_data','planoContas_id','filial_id','valor')
 'fPrevisao'=@('competencia_data','planoContas_id','filial_id','valor')
 'dPlanoConta'=@('id','index','mascaraDRE_id','tipoLancamento','detalharN2')
 'dFilial'=@('id')
 'dEstruturaDRE'=@('id','index','subtotal')
 'dCalendario'=@('AnoAtual','MesAtual')
 'dDRE'=@('Ordem','Subtotal')
}

function Find-Measure($name){ foreach($t in $model.Tables){ $m=$t.Measures.Find($name); if($m){ return $m } }; $null }
$n=@{legado=0;desc=0;cols=0}
foreach($name in $legado){ $m=Find-Measure $name; if(-not $m){throw "Medida não encontrada: $name"}; $m.DisplayFolder='_Legado'; $m.IsHidden=$true; $n.legado++ }
foreach($k in $desc.Keys){ $m=Find-Measure $k; if(-not $m){throw "Medida não encontrada: $k"}; $m.Description=$desc[$k]; $n.desc++ }
foreach($t in $hide.Keys){ foreach($c in $hide[$t]){ $col=$model.Tables[$t].Columns.Find($c); if(-not $col){throw "Coluna não encontrada: $t[$c]"}; $col.IsHidden=$true; $n.cols++ } }
$ctx=$f.Measures.Find('Contexto Executivo')
$ctx.Expression=@'
VAR AnoMin = MIN(dCalendario[Ano])
VAR AnoMax = MAX(dCalendario[Ano])
VAR Anos = IF(AnoMin = AnoMax, FORMAT(AnoMin, "0"), FORMAT(AnoMin, "0") & "–" & FORMAT(AnoMax, "0"))
RETURN "XPBucks • " & Anos & " • " & IF(HASONEVALUE(dFilial[Filial]), SELECTEDVALUE(dFilial[Filial]), "Filiais selecionadas") & " • " & FORMAT([Meses Realizados no Contexto], "0") & " meses com realizado"
'@
if($WhatIf){ "WHATIF: $($n.legado) legado, $($n.desc) descrições, $($n.cols) colunas"; $model.UndoLocalChanges(); return }
$model.SaveChanges() | Out-Null
$server.Disconnect()
"OK: $($n.legado) medidas em _Legado (ocultas), $($n.desc) descrições, $($n.cols) colunas ocultas, Contexto Executivo dinâmico. Salve no Desktop."
