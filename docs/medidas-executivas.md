# Catálogo de medidas executivas

68 medidas auxiliares em fLancamentos, somadas às 76 medidas originais: 144 no total. As 95 medidas usadas pelo relatório (direta ou indiretamente) ficam visíveis em suas pastas; as 49 sem uso foram movidas para a pasta oculta `_Legado`, sem exclusão. As principais têm descrição no próprio modelo. Regras de cobertura e comparabilidade: [regras de negócio](regras-negocio.md).

## Meses Realizados no Contexto

Pasta: `Executivo/Cobertura`. Formato: `0`.

```dax
COUNTROWS(CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE)))
```

## Comparação AA Disponível

Pasta: `Executivo/Cobertura`. Formato: `0`.

```dax
VAR Atual = CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE))
VAR Anterior = SELECTCOLUMNS(Atual,"DataAA",EDATE(fLancamentos[competencia_data],-12))
VAR Existe = CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dCalendario), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE), TREATAS(Anterior,dCalendario[Data]))
RETURN IF(HASONEVALUE(dCalendario[Ano]) && COUNTROWS(Atual)>0 && COUNTROWS(Existe)=COUNTROWS(Atual),1,0)
```

## Orçamento Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Datas = CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE))
RETURN IF(COUNTROWS(Datas)>0, CALCULATE([Valor Orçado], KEEPFILTERS(TREATAS(Datas,dCalendario[Data]))))
```

## Impacto Orçamentário R$

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Real = [Valor Realizado]
VAR Orc = [Orçamento Comparável]
RETURN IF(NOT ISBLANK(Real) && NOT ISBLANK(Orc), Real-Orc)
```

## Impacto Orçamentário %

Pasta: `Executivo`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([Impacto Orçamentário R$],ABS([Orçamento Comparável]))
```

## Cor Impacto Orçamentário

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V = [Impacto Orçamentário R$]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Receita Líquida Orçamento Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
CALCULATE([Orçamento Comparável],KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2}))
```

## Receita Líquida AA Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Datas = CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE))
VAR Anterior = SELECTCOLUMNS(Datas,"DataAA",EDATE(fLancamentos[competencia_data],-12))
RETURN IF([Comparação AA Disponível]=1,CALCULATE([Receita Líquida],REMOVEFILTERS(dCalendario),TREATAS(Anterior,dCalendario[Data])))
```

## Receita Líquida Δ AA

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Receita Líquida]) && NOT ISBLANK([Receita Líquida AA Comparável]), [Receita Líquida]-[Receita Líquida AA Comparável])
```

## Receita Líquida Δ Orçamento

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Receita Líquida]) && NOT ISBLANK([Receita Líquida Orçamento Comparável]), [Receita Líquida]-[Receita Líquida Orçamento Comparável])
```

## Receita Líquida Comparativos

Pasta: `Executivo/Cartões`. Formato: `texto`.

```dax
VAR AA = [Receita Líquida Δ AA]
VAR Orc = [Receita Líquida Δ Orçamento]
VAR AAPct = DIVIDE(AA,ABS([Receita Líquida AA Comparável]))
VAR OrcPct = DIVIDE(Orc,ABS([Receita Líquida Orçamento Comparável]))
RETURN IF(ISBLANK([Receita Líquida]),"Sem realizado no período",
IF(ISBLANK(AA),"AA: comparação indisponível", "AA: " & FORMAT(AA/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(AAPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"Orçamento indisponível", "Orç: " & FORMAT(Orc/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(OrcPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"",IF(Orc>0,"↑ Favorável vs orçamento",IF(Orc<0,"↓ Desfavorável vs orçamento","Em linha com orçamento"))))
```

## Receita Líquida Cor Executivo

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[Receita Líquida Δ Orçamento]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Lucro Bruto Orçamento Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
CALCULATE([Orçamento Comparável],KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2,4}))
```

## Lucro Bruto AA Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Datas = CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE))
VAR Anterior = SELECTCOLUMNS(Datas,"DataAA",EDATE(fLancamentos[competencia_data],-12))
RETURN IF([Comparação AA Disponível]=1,CALCULATE([Lucro Bruto],REMOVEFILTERS(dCalendario),TREATAS(Anterior,dCalendario[Data])))
```

## Lucro Bruto Δ AA

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Lucro Bruto]) && NOT ISBLANK([Lucro Bruto AA Comparável]), [Lucro Bruto]-[Lucro Bruto AA Comparável])
```

## Lucro Bruto Δ Orçamento

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Lucro Bruto]) && NOT ISBLANK([Lucro Bruto Orçamento Comparável]), [Lucro Bruto]-[Lucro Bruto Orçamento Comparável])
```

## Lucro Bruto Comparativos

Pasta: `Executivo/Cartões`. Formato: `texto`.

```dax
VAR AA = [Lucro Bruto Δ AA]
VAR Orc = [Lucro Bruto Δ Orçamento]
VAR AAPct = DIVIDE(AA,ABS([Lucro Bruto AA Comparável]))
VAR OrcPct = DIVIDE(Orc,ABS([Lucro Bruto Orçamento Comparável]))
RETURN IF(ISBLANK([Lucro Bruto]),"Sem realizado no período",
IF(ISBLANK(AA),"AA: comparação indisponível", "AA: " & FORMAT(AA/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(AAPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"Orçamento indisponível", "Orç: " & FORMAT(Orc/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(OrcPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"",IF(Orc>0,"↑ Favorável vs orçamento",IF(Orc<0,"↓ Desfavorável vs orçamento","Em linha com orçamento"))))
```

## Lucro Bruto Cor Executivo

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[Lucro Bruto Δ Orçamento]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Resultado Operacional Orçamento Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
CALCULATE([Orçamento Comparável],KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2,4,6,9}))
```

## Resultado Operacional AA Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Datas = CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE))
VAR Anterior = SELECTCOLUMNS(Datas,"DataAA",EDATE(fLancamentos[competencia_data],-12))
RETURN IF([Comparação AA Disponível]=1,CALCULATE([Resultado Operacional],REMOVEFILTERS(dCalendario),TREATAS(Anterior,dCalendario[Data])))
```

## Resultado Operacional Δ AA

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Resultado Operacional]) && NOT ISBLANK([Resultado Operacional AA Comparável]), [Resultado Operacional]-[Resultado Operacional AA Comparável])
```

## Resultado Operacional Δ Orçamento

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Resultado Operacional]) && NOT ISBLANK([Resultado Operacional Orçamento Comparável]), [Resultado Operacional]-[Resultado Operacional Orçamento Comparável])
```

## Resultado Operacional Comparativos

Pasta: `Executivo/Cartões`. Formato: `texto`.

```dax
VAR AA = [Resultado Operacional Δ AA]
VAR Orc = [Resultado Operacional Δ Orçamento]
VAR AAPct = DIVIDE(AA,ABS([Resultado Operacional AA Comparável]))
VAR OrcPct = DIVIDE(Orc,ABS([Resultado Operacional Orçamento Comparável]))
RETURN IF(ISBLANK([Resultado Operacional]),"Sem realizado no período",
IF(ISBLANK(AA),"AA: comparação indisponível", "AA: " & FORMAT(AA/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(AAPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"Orçamento indisponível", "Orç: " & FORMAT(Orc/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(OrcPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"",IF(Orc>0,"↑ Favorável vs orçamento",IF(Orc<0,"↓ Desfavorável vs orçamento","Em linha com orçamento"))))
```

## Resultado Operacional Cor Executivo

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[Resultado Operacional Δ Orçamento]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Resultado Líquido Orçamento Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
CALCULATE([Orçamento Comparável],KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2,4,6,7,9,10,12}))
```

## Resultado Líquido AA Comparável

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Datas = CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE))
VAR Anterior = SELECTCOLUMNS(Datas,"DataAA",EDATE(fLancamentos[competencia_data],-12))
RETURN IF([Comparação AA Disponível]=1,CALCULATE([Resultado Líquido],REMOVEFILTERS(dCalendario),TREATAS(Anterior,dCalendario[Data])))
```

## Resultado Líquido Δ AA

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Resultado Líquido]) && NOT ISBLANK([Resultado Líquido AA Comparável]), [Resultado Líquido]-[Resultado Líquido AA Comparável])
```

## Resultado Líquido Δ Orçamento

Pasta: `Executivo`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Resultado Líquido]) && NOT ISBLANK([Resultado Líquido Orçamento Comparável]), [Resultado Líquido]-[Resultado Líquido Orçamento Comparável])
```

## Resultado Líquido Comparativos

Pasta: `Executivo/Cartões`. Formato: `texto`.

```dax
VAR AA = [Resultado Líquido Δ AA]
VAR Orc = [Resultado Líquido Δ Orçamento]
VAR AAPct = DIVIDE(AA,ABS([Resultado Líquido AA Comparável]))
VAR OrcPct = DIVIDE(Orc,ABS([Resultado Líquido Orçamento Comparável]))
RETURN IF(ISBLANK([Resultado Líquido]),"Sem realizado no período",
IF(ISBLANK(AA),"AA: comparação indisponível", "AA: " & FORMAT(AA/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(AAPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"Orçamento indisponível", "Orç: " & FORMAT(Orc/1000000,"+0.00;-0.00;0.00","pt-BR") & " mi (" & FORMAT(OrcPct,"+0.0%;-0.0%;0.0%","pt-BR") & ")") & UNICHAR(10) &
IF(ISBLANK(Orc),"",IF(Orc>0,"↑ Favorável vs orçamento",IF(Orc<0,"↓ Desfavorável vs orçamento","Em linha com orçamento"))))
```

## Resultado Líquido Cor Executivo

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[Resultado Líquido Δ Orçamento]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Margem Bruta AA Comparável

Pasta: `Executivo`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([Lucro Bruto AA Comparável],[Receita Líquida AA Comparável])
```

## Margem Bruta Orçamento Comparável

Pasta: `Executivo`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([Lucro Bruto Orçamento Comparável],[Receita Líquida Orçamento Comparável])
```

## Margem Bruta Δ AA p.p.

Pasta: `Executivo`. Formato: `0.0" p.p.";(0.0)" p.p.";0.0" p.p."`.

```dax
IF(NOT ISBLANK([Margem Bruta %]) && NOT ISBLANK([Margem Bruta AA Comparável]),100*([Margem Bruta %]-[Margem Bruta AA Comparável]))
```

## Margem Bruta Δ Orçamento p.p.

Pasta: `Executivo`. Formato: `0.0" p.p.";(0.0)" p.p.";0.0" p.p."`.

```dax
IF(NOT ISBLANK([Margem Bruta %]) && NOT ISBLANK([Margem Bruta Orçamento Comparável]),100*([Margem Bruta %]-[Margem Bruta Orçamento Comparável]))
```

## Margem Bruta Comparativos

Pasta: `Executivo/Cartões`. Formato: `texto`.

```dax
VAR AA=[Margem Bruta Δ AA p.p.]
VAR Orc=[Margem Bruta Δ Orçamento p.p.]
RETURN IF(ISBLANK([Margem Bruta %]),"Sem realizado no período",
IF(ISBLANK(AA),"AA: comparação indisponível","AA: " & FORMAT(AA,"+0.0;-0.0;0.0","pt-BR") & " p.p.") & UNICHAR(10) &
IF(ISBLANK(Orc),"Orçamento indisponível","Orç: " & FORMAT(Orc,"+0.0;-0.0;0.0","pt-BR") & " p.p.") & UNICHAR(10) & IF(ISBLANK(Orc),"",IF(Orc>0,"↑ Favorável vs orçamento",IF(Orc<0,"↓ Desfavorável vs orçamento","Em linha com orçamento"))))
```

## Margem Bruta Cor Executivo

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[Margem Bruta Δ Orçamento p.p.]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Margem Líquida AA Comparável

Pasta: `Executivo`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([Resultado Líquido AA Comparável],[Receita Líquida AA Comparável])
```

## Margem Líquida Orçamento Comparável

Pasta: `Executivo`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([Resultado Líquido Orçamento Comparável],[Receita Líquida Orçamento Comparável])
```

## Margem Líquida Δ AA p.p.

Pasta: `Executivo`. Formato: `0.0" p.p.";(0.0)" p.p.";0.0" p.p."`.

```dax
IF(NOT ISBLANK([Margem Líquida %]) && NOT ISBLANK([Margem Líquida AA Comparável]),100*([Margem Líquida %]-[Margem Líquida AA Comparável]))
```

## Margem Líquida Δ Orçamento p.p.

Pasta: `Executivo`. Formato: `0.0" p.p.";(0.0)" p.p.";0.0" p.p."`.

```dax
IF(NOT ISBLANK([Margem Líquida %]) && NOT ISBLANK([Margem Líquida Orçamento Comparável]),100*([Margem Líquida %]-[Margem Líquida Orçamento Comparável]))
```

## Margem Líquida Comparativos

Pasta: `Executivo/Cartões`. Formato: `texto`.

```dax
VAR AA=[Margem Líquida Δ AA p.p.]
VAR Orc=[Margem Líquida Δ Orçamento p.p.]
RETURN IF(ISBLANK([Margem Líquida %]),"Sem realizado no período",
IF(ISBLANK(AA),"AA: comparação indisponível","AA: " & FORMAT(AA,"+0.0;-0.0;0.0","pt-BR") & " p.p.") & UNICHAR(10) &
IF(ISBLANK(Orc),"Orçamento indisponível","Orç: " & FORMAT(Orc,"+0.0;-0.0;0.0","pt-BR") & " p.p.") & UNICHAR(10) & IF(ISBLANK(Orc),"",IF(Orc>0,"↑ Favorável vs orçamento",IF(Orc<0,"↓ Desfavorável vs orçamento","Em linha com orçamento"))))
```

## Margem Líquida Cor Executivo

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[Margem Líquida Δ Orçamento p.p.]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Receita Desvio Orçamento %

Pasta: `Executivo`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([Receita Líquida Δ Orçamento],ABS([Receita Líquida Orçamento Comparável]))
```

## Resultado Desvio Orçamento %

Pasta: `Executivo`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([Resultado Líquido Δ Orçamento],ABS([Resultado Líquido Orçamento Comparável]))
```

## DRE Base Orçamento Comparável

Pasta: `Executivo/DRE`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Detalhe = ISINSCOPE(dPlanoConta[descricaoN1]) || ISINSCOPE(dPlanoConta[descricaoN2])
VAR Subtotal = SELECTEDVALUE(dDRE[Subtotal], 0)
RETURN IF(Detalhe && Subtotal = 1, BLANK(), SWITCH(SELECTEDVALUE(dDRE[Ordem]),
1, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1})),
2, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {2})),
3, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2})),
4, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {4})),
5, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2,4})),
6, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {6})),
7, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {7})),
8, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2,4,6,7})),
9, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {9})),
10, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {10})),
11, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2,4,6,7,9,10})),
12, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {12})),
13, CALCULATE([Orçamento Comparável], KEEPFILTERS(dPlanoConta[GrupoDRE] IN {1,2,4,6,7,9,10,12})), BLANK()))
```

## DRE Orçamento Comparável

Pasta: `Executivo/DRE`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
SWITCH(SELECTEDVALUE(dPeriodo[Modo],"Seleção"),"Acumulado no ano",CALCULATE([DRE Base Orçamento Comparável],DATESYTD(dCalendario[Data])),"Ano completo",CALCULATE([DRE Base Orçamento Comparável],REMOVEFILTERS(dCalendario),VALUES(dCalendario[Ano])),[DRE Base Orçamento Comparável])
```

## DRE Impacto Orçamentário R$

Pasta: `Executivo/DRE`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([DRE Realizado]) && NOT ISBLANK([DRE Orçamento Comparável]),[DRE Realizado]-[DRE Orçamento Comparável])
```

## DRE Impacto Orçamentário %

Pasta: `Executivo/DRE`. Formato: `0.0%;(0.0%);0.0%`.

```dax
DIVIDE([DRE Impacto Orçamentário R$],ABS([DRE Orçamento Comparável]))
```

## DRE Cor Orçamento

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[DRE Impacto Orçamentário R$]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## DRE Base AA Comparável

Pasta: `Executivo/DRE`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
VAR Datas=CALCULATETABLE(VALUES(fLancamentos[competencia_data]), REMOVEFILTERS(dPlanoConta), REMOVEFILTERS(dEstruturaDRE), REMOVEFILTERS(dDRE))
VAR Anterior=SELECTCOLUMNS(Datas,"DataAA",EDATE(fLancamentos[competencia_data],-12))
RETURN IF([Comparação AA Disponível]=1,CALCULATE([DRE Base Realizado],REMOVEFILTERS(dCalendario),TREATAS(Anterior,dCalendario[Data])))
```

## DRE AA Comparável

Pasta: `Executivo/DRE`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
SWITCH(SELECTEDVALUE(dPeriodo[Modo],"Seleção"),"Acumulado no ano",CALCULATE([DRE Base AA Comparável],DATESYTD(dCalendario[Data])),"Ano completo",CALCULATE([DRE Base AA Comparável],REMOVEFILTERS(dCalendario),VALUES(dCalendario[Ano])),[DRE Base AA Comparável])
```

## DRE AH Comparável %

Pasta: `Executivo/DRE`. Formato: `0.0%;(0.0%);0.0%`.

```dax
IF(NOT ISBLANK([DRE Realizado]) && NOT ISBLANK([DRE AA Comparável]),DIVIDE([DRE Realizado]-[DRE AA Comparável],ABS([DRE AA Comparável])))
```

## DRE Resultado Operacional

Pasta: `Executivo/DRE`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
SWITCH(SELECTEDVALUE(dPeriodo[Modo],"Seleção"),"Acumulado no ano",CALCULATE([Resultado Operacional],DATESYTD(dCalendario[Data])),"Ano completo",CALCULATE([Resultado Operacional],REMOVEFILTERS(dCalendario),VALUES(dCalendario[Ano])),[Resultado Operacional])
```

## DRE Impacto Conta R$

Pasta: `Executivo/DRE`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
SWITCH(SELECTEDVALUE(dPeriodo[Modo],"Seleção"),"Acumulado no ano",CALCULATE([Impacto Orçamentário R$],DATESYTD(dCalendario[Data])),"Ano completo",CALCULATE([Impacto Orçamentário R$],REMOVEFILTERS(dCalendario),VALUES(dCalendario[Ano])),[Impacto Orçamentário R$])
```

## DRE Impacto Conta %

Pasta: `Executivo/DRE`. Formato: `0.0%;(0.0%);0.0%`.

```dax
SWITCH(SELECTEDVALUE(dPeriodo[Modo],"Seleção"),"Acumulado no ano",CALCULATE([Impacto Orçamentário %],DATESYTD(dCalendario[Data])),"Ano completo",CALCULATE([Impacto Orçamentário %],REMOVEFILTERS(dCalendario),VALUES(dCalendario[Ano])),[Impacto Orçamentário %])
```

## DRE Cor Impacto Conta

Pasta: `Executivo/Formatação`. Formato: `texto`.

```dax
VAR V=[DRE Impacto Conta R$]
RETURN IF(ISBLANK(V),"#454545",IF(V>=0,"#254B3F","#A33F36"))
```

## Ranking Impacto Conta

Pasta: `Executivo/Desvios`. Formato: `0`.

```dax
VAR V=[DRE Impacto Conta R$]
RETURN IF(NOT ISBLANK(V), RANKX(ALLSELECTED(dPlanoConta[descricaoN2]),ABS([DRE Impacto Conta R$]),ABS(V),DESC,Dense))
```

## Top 8 Impacto Conta

Pasta: `Executivo/Desvios`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF([Ranking Impacto Conta]<=8 && NOT ISBLANK([Ranking Impacto Conta]),[DRE Impacto Conta R$])
```

## Componente Waterfall DRE

Pasta: `Executivo/Waterfall`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(SELECTEDVALUE(dDRE[Ordem]) IN {3,4,6,7,9,10,12},[DRE Realizado])
```

## Resultado Mensal Negativo

Pasta: `Executivo/Gráficos`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF([Resultado Líquido]<0,[Resultado Líquido])
```

## Referência Zero

Pasta: `Executivo/Gráficos`. Formato: `"R$" #,##0.00;("R$" #,##0.00);"R$" 0.00`.

```dax
IF(NOT ISBLANK([Resultado Líquido]) || NOT ISBLANK([Resultado Líquido Orçada]),0)
```

## Contexto Executivo

Pasta: `Executivo/Texto`. Formato: `texto`. Faixa de anos calculada pelo calendário filtrado (desde 09/11/2026); no contexto padrão o texto é o mesmo de antes.

```dax
VAR AnoMin = MIN(dCalendario[Ano])
VAR AnoMax = MAX(dCalendario[Ano])
VAR Anos = IF(AnoMin = AnoMax, FORMAT(AnoMin, "0"), FORMAT(AnoMin, "0") & "–" & FORMAT(AnoMax, "0"))
RETURN "XPBucks • " & Anos & " • " & IF(HASONEVALUE(dFilial[Filial]), SELECTEDVALUE(dFilial[Filial]), "Filiais selecionadas") & " • " & FORMAT([Meses Realizados no Contexto], "0") & " meses com realizado"
```

## Insight Receita

Pasta: `Executivo/Insights`. Formato: `texto`.

```dax
VAR V=[Receita Líquida Δ Orçamento]
RETURN IF(ISBLANK(V),"Receita: comparação orçamentária indisponível.","Receita " & IF(V>=0,"acima","abaixo") & " do orçamento em " & FORMAT(ABS(V)/1000000,"0.00","pt-BR") & " mi, nos meses com realizado.")
```

## Insight Margem

Pasta: `Executivo/Insights`. Formato: `texto`.

```dax
VAR V=[Margem Bruta Δ AA p.p.]
RETURN IF(ISBLANK(V),"Margem: selecione um ano com base anterior comparável.","Margem bruta " & IF(V>=0,"aumentou ","diminuiu ") & FORMAT(ABS(V),"0.0","pt-BR") & " p.p. frente aos mesmos meses do ano anterior.")
```

## Insight Custos

Pasta: `Executivo/Insights`. Formato: `texto`.

```dax
VAR V=CALCULATE([Impacto Orçamentário R$],KEEPFILTERS(dPlanoConta[GrupoDRE]=4))
RETURN IF(ISBLANK(V),"Custos: comparação indisponível.","Custos: impacto " & IF(V>=0,"favorável","desfavorável") & " de " & FORMAT(ABS(V)/1000000,"0.00","pt-BR") & " mi frente ao orçamento comparável.")
```

## Insight Filial

Pasta: `Executivo/Insights`. Formato: `texto`.

```dax
VAR T=FILTER(ADDCOLUMNS(ALLSELECTED(dFilial[Filial]),"Valor",[Resultado Líquido]),NOT ISBLANK([Valor]))
VAR Lider=TOPN(1,T,[Valor],DESC,dFilial[Filial],ASC)
RETURN IF(COUNTROWS(T)=0,"Filiais: sem realizado no contexto.","Maior resultado entre as filiais selecionadas: " & CONCATENATEX(Lider,dFilial[Filial],", ") & " (R$ " & FORMAT(MAXX(Lider,[Valor])/1000000,"0.00","pt-BR") & " mi).")
```

## Insight Despesa

Pasta: `Executivo/Insights`. Formato: `texto`.

```dax
VAR T=CALCULATETABLE(ADDCOLUMNS(ALLSELECTED(dPlanoConta[descricaoN2]),"Impacto",[DRE Impacto Conta R$]),KEEPFILTERS(dPlanoConta[GrupoDRE]=6))
VAR Neg=FILTER(T,NOT ISBLANK([Impacto]) && [Impacto]<0)
VAR Lider=TOPN(1,Neg,[Impacto],ASC,dPlanoConta[descricaoN2],ASC)
RETURN IF(ISBLANK([DRE Resultado Operacional]),"Despesas: sem realizado no contexto.",IF(COUNTROWS(Neg)=0,"Nenhum desvio desfavorável de despesa no contexto comparável.","Maior desvio desfavorável de despesa: " & CONCATENATEX(Lider,dPlanoConta[descricaoN2],", ") & " (R$ " & FORMAT(ABS(MINX(Lider,[Impacto]))/1000,"0.0","pt-BR") & " mil)."))
```

## Síntese Executiva

Pasta: `Executivo/Insights`. Formato: `texto`.

```dax
[Insight Receita] & UNICHAR(10) & [Insight Margem] & UNICHAR(10) & [Insight Filial]
```
