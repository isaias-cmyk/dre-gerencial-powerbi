# Auditoria XPBucks — cobertura e medidas

> As contagens abaixo (26 tabelas, 37 relacionamentos, 76 medidas) descrevem o modelo em 02/11/2026. Depois disso o modelo ganhou as medidas executivas (144 no total) e foi simplificado em 09/11/2026 para 9 tabelas e 10 relacionamentos, com a mesma regressão aprovada. O estado atual está no [README](../README.md#data-validation--quality-assurance).

Auditoria iniciada em 01/11/2026 e concluída em 02/11/2026. Escopo confirmado: exclusivamente fontes e tabelas existentes, nomes preservados, histórico encerrado em 31/12/2023. Nenhuma fonte nova ou registro fictício foi criado.

## Cobertura confirmada antes das alterações

| Fonte existente | Linhas | Competências originais | Resultado |
|---|---:|---|---|
| fLancamento1_ano1, fLancamento2_ano1, fLancamento3_ano1 | 516 cada | jan–dez/2021 | 43 contas por mês em cada aba |
| fLancamento1_ano2, fLancamento2_ano2, fLancamento3_ano2 | 516 cada | jan–dez/2022 | 43 contas por mês em cada aba |
| fLancamento1_ano3, fLancamento2_ano3, fLancamento3_ano3 | 215 cada | jan–mai/2023 | 43 contas por mês em cada aba |
| fLancamentos | 3.741 | jan/2021–mai/2023 | União das nove fontes, 129 contas por mês |
| fPrevisao | 4.644 | jan/2021–dez/2023 | 129 contas por mês |
| fOrcamento | 4.644 | jan/2021–dez/2023 | 129 contas por mês |

As datas armazenadas são o primeiro dia da competência: 01/05/2023 representa maio, e 01/12/2023 representa dezembro. O calendário termina em 31/12/2023. As dimensões de contas, estrutura, filiais e auxiliares de cadastro não representam movimentos temporais; dDRE e dPeriodo são seletores de apresentação.

Método: releitura do Excel original referenciado pelas consultas, comparação de todas as chaves/datas/valores com a cópia tratada e consulta DAX direta das 12 tabelas, sem filtros do relatório. As 188 combinações tabela/competência coincidiram exatamente. Diferença máxima de reserialização dos valores Excel: R$ 0,0000000004656613, inferior à tolerância de R$ 0,00000001. Os hashes das duas planilhas estão no artefato local cobertura-fontes.json.

Conclusão: o realizado termina em maio/2023 **na própria origem**, nas três filiais. Não há perda de junho–dezembro causada por carregamento, relacionamentos ou filtros. Essa cobertura é uma característica da base histórica entregue, não uma pendência de atualização.

## Auditoria DAX e correção

As 76 medidas foram inventariadas e suas dependências revisadas. A correção altera somente três expressões, preservando nomes, lineageTags e formatos:

| Medida | Problema reproduzido | Correção |
|---|---|---|
| Crescimento Receita % | junho/2023 sem realizado retornava −100% | Branco se valor atual ou anterior está ausente |
| Variação YoY % | mesmo problema para resultado líquido | Mesma guarda ISBLANK |
| DRE AH % | mesmo problema na matriz | Mesma guarda ISBLANK |

Valores efetivamente existentes continuam usando `(atual − anterior) / ABS(anterior)`, com DIVIDE e branco quando o denominador é zero. Nenhuma conta, sinal, subtotal, margem, granularidade ou regra de comparação foi reclassificada. As outras 73 medidas e todas as consultas M permaneceram inalteradas. A auditoria verificou essa restrição comparando os arquivos antes/depois, além dos testes numéricos.

Foram conferidos AV no nível de grupo de contas, meses alternados (janeiro e março/2022), datas/filiais combinadas, YTD, ano completo, ausência de base anterior, totais e todas as linhas DRE. MTD/YTD usam o contexto do calendário; sem seleção de data, o limite é dezembro/2023, mesmo sem realizado nesse mês. Para YTD, manter seleção de um único ano. O atingimento sem filtro continua comparando a disponibilidade integral de cada cenário, como documentado; não foi alterado para excluir meses silenciosamente.

## Apresentação e preservação

Mantidas as cinco páginas, 71 visuais, IDs, posições e vinculações. Cabeçalhos abreviados e amigáveis não renomeiam objetos do modelo. Cartões usam fonte menor para acomodar valores negativos. A matriz usa as medidas existentes DRE Cor Desvio e DRE Cor Linha: verde/vermelho nos desvios e destaque dos subtotais. O cabeçalho das páginas explicita o fechamento histórico e a cobertura realizada.

As páginas de preparação já estavam removidas no início desta revisão. Essa alteração anterior foi preservada; não houve exclusão adicional. Permanecem 26 tabelas e 37 relacionamentos, sem mudanças de topologia ou cardinalidade.

## Evidências e testes

- `tests/audit_source_coverage.py`: original × tratado e geração da consulta de cobertura.
- `scripts/read_dax.ps1`: consultas de leitura no Desktop; nenhuma atualização via XMLA/TOM.
- `tests/check_audit_results.py`: 188 competências, 324 verificações de percentuais em 108 contextos, cores válidas e comparação de estrutura antes/depois.
- `tests/check_calendar_live.ps1`: calendário, somas anuais, mês sem realizado e filtros.
- `tests/check_dre_live.ps1`: 2.424 agregações e 2.535 resultados DRE, além de AV/YTD/ano completo/brancos. Maior diferença de conciliação: R$ 0,00000001; tolerância R$ 0,01.
- `scripts/validate_tmdl.ps1`: TOM aprovado, 26 tabelas/37 relações.
- `scripts/validate_project.py`: PBIR aprovado nos schemas oficiais; permanece HTTP 404 no schema do localSettings.json preexistente, preservado.

Os resultados detalhados de cada execução são gerados localmente em `artifacts/auditoria` (pasta de trabalho, fora do repositório); os scripts acima recriam essas evidências. O teste de comparação exige evidências geradas na mesma execução.

Referências oficiais: [ISBLANK](https://learn.microsoft.com/en-us/dax/isblank-function-dax), [ISINSCOPE](https://learn.microsoft.com/en-us/dax/isinscope-function-dax), [DATEADD](https://learn.microsoft.com/en-us/dax/dateadd-function-dax), [formatação PBIR por campo](https://github.com/microsoft/skills-for-fabric/blob/main/skills/powerbi-report-cli/references/authoring/conditional-formatting-part-07.md).
