# Controladoria XPBucks — base de modelagem

## Especificação lida

Fonte: Contexto Projeto.pptx, slides 1–4. Público: diretoria. Escopo: DRE, receita, despesas, margem, resultado líquido, evolução desde 2021, comparação por filial e com previsão. São Paulo, Rio de Janeiro e Florianópolis constam no contexto. O prazo 11/12/2023 é histórico, não uma nova data de entrega.

O briefing é especificação de negócio. Não contém autorização para envio de mensagens, publicação ou mudanças fora deste workspace. A implementação usa a estrutura de 13 linhas da fonte e o sinal tipoLancamento do cadastro, conciliados com agregações independentes do Excel original.

## Contrato de dados

- Excel original preservado. Cópia tratada: data/processed/BaseDados_Tratada.xlsx, excluída do Git.
- Dimensão de contas: 129 chaves textuais; estrutura DRE: 39 chaves textuais; filiais: 3. Códigos com pontos e zeros à esquerda não são datas nem decimais.
- Fatos na granularidade competência mensal × conta. Todas as datas são início do mês. O cadastro de contas distingue filiais pelo prefixo, validado contra a coluna empresa da estrutura.
- Realizado: nove abas consolidadas em fLancamentos, 3.741 registros. 2021: 1.548; 2022: 1.548; 2023: 645, até maio.
- Orçamento e previsão: 4.644 registros cada, de janeiro/2021 a dezembro/2023.
- Nenhuma duplicidade de competência/conta nem chave órfã encontrada nas fatos. As quantias são preservadas, sem arredondar os dados de origem; formatação com duas casas não altera o valor armazenado.
- Removidas da cópia tratada linhas completamente vazias e colunas sem cabeçalho fora da estrutura DRE. Conteúdo de negócio não foi excluído. As tabelas auxiliares Table_1…Table_8 foram removidas em 09/11/2026 (scripts/simplify_model.py): estavam ocultas, sem uso em visuais, medidas ou relacionamentos, e dependiam de um caminho absoluto do Excel original.

## Modelo

- dCalendario[Data] → competencia_data das fatos, cardinalidade 1:* e filtro único da dimensão para os fatos.
- dPlanoConta[id] → planoContas_id das fatos, 1:* unidirecional.
- dFilial[id] → filial_id das fatos, 1:* unidirecional.
- dEstruturaDRE[id] → dPlanoConta[mascaraDRE_id], 1:* unidirecional. É uma extensão normalizada do cadastro para preservar a estrutura gerencial existente.
- As nove consultas de origem (fLancamentoX_anoY) são staging sem carga desde 09/11/2026: existem apenas no Power Query e alimentam **fLancamentos**, única fato de realizado no modelo. Isso eliminou 27 relacionamentos e o risco de somar a consolidada com as origens.
- Medidas básicas: Valor Realizado, Valor Orçado, Valor Previsto = SUMX da respectiva fato, valor × RELATED(dPlanoConta[tipoLancamento]); Registros Realizados = quantidade de linhas. Nenhuma medida básica é, por si só, receita, lucro ou margem. SUM(valor) permanece disponível apenas para conciliação dos montantes brutos.

## DRE e indicadores implementados

O modelo tem dDRE e dPeriodo desconectadas para apresentação. GrupoDRE é extraído da máscara real de cada conta. Não foram criados relacionamentos entre fatos ou filtros bidirecionais.

| Linha | Composição por GrupoDRE |
|---|---|
| Receita operacional bruta | 1 |
| Deduções | 2 |
| Receita líquida | 1 + 2 |
| Custos | 4 |
| Lucro bruto | 1 + 2 + 4 |
| Despesas operacionais | 6 |
| Resultado financeiro | 7 |
| Resultado após despesas e financeiro | 1 + 2 + 4 + 6 + 7 |
| Depreciação/amortização | 9 |
| Outras receitas/despesas | 10 |
| Resultado antes dos tributos | 1 + 2 + 4 + 6 + 7 + 9 + 10 |
| Provisão IR/CSLL | 12 |
| Resultado líquido | 1 + 2 + 4 + 6 + 7 + 9 + 10 + 12 |

Valores negativos de origem são preservados, inclusive 18 movimentos realizados e 20 em cada cenário planejado de IR/CSLL. Não se aplica ABS aos movimentos: a natureza negativa da conta inverte também essas reversões. A linha 8 não é denominada EBITDA. Resultado Operacional usa grupos 1,2,4,6,9 e exclui financeiro e outras receitas/despesas; essa definição é explícita, sem reclassificar contas.

Margem bruta = lucro bruto / receita líquida; margem líquida = resultado líquido / receita líquida. Atingimento = receita líquida / receita líquida orçada. DIVIDE devolve branco para denominador zero/ausente. Desvio = realizado − previsto; percentuais de variação usam ABS do comparador para manter o sentido favorável/desfavorável com despesas assinadas. Sem realizado, os desvios ficam em branco.

AV divide a linha pela receita líquida do mesmo contexto temporal/filial. AH compara com o mesmo período do ano anterior; 2021 não tem base anterior. AH, Crescimento Receita % e Variação YoY % retornam branco quando falta realizado atual ou comparador; ausência não é queda de 100%. A matriz não soma subtotais no total geral e não repete subtotais no detalhamento de contas. dPeriodo seleciona contexto atual, acumulado no ano ou ano completo; para YTD recomenda-se selecionar um único ano. Ano completo remove filtros de mês/dia mantendo os anos selecionados.

O período dos cenários difere. Sem filtro, os KPIs somam toda a disponibilidade e a razão com orçamento inclui junho–dezembro/2023, sem realizado na fonte. Para comparação de execução, selecione o mesmo período com realizado (até maio/2023). Não interpretar a razão geral como execução integral de 2023. Não há pendência de obter dados além do encerramento histórico em 31/12/2023.

As fontes existentes são lançamentos gerenciais mensais, orçamento e previsão. O escopo histórico termina em 31/12/2023; não há demanda por períodos posteriores. Preservar os nomes atuais e não adicionar fontes.

## Calendário

Adaptado a partir de dCalendario.txt, que referenciava uma fLancamentos ainda inexistente. Usa a menor e maior data entre realizado, orçamento e previsão, expandidas para anos completos. Nesta base: 01/01/2021–31/12/2023, 1.095 dias únicos, contínuos e sem nulos.

Data é a chave e a tabela recebe dataCategory Time. NomeMes/MesAbre ordenam por MesNum; MesAno por AnoMesINT. Nomes em pt-BR, semana iniciando na segunda-feira; Semana usa semana do ano (não semana do mês nem calendário ISO). AnoAtual/MesAtual usam data de atualização em UTC−3; não significam último ano/mês disponível na base histórica.

dataPassada indica competência até o fim do último mês realizado, inclusive. Não inclui meses apenas previstos. Filtros oficiais devem usar dCalendario[Ano], [MesAno], [Data] ou a hierarquia Calendário. Não usar antigas hierarquias automáticas.

## Impacto da substituição dos calendários automáticos

Foram analisadas referências no relatório: nenhum visual usa LocalDateTable ou DateTableTemplate. Os 25 calendários automáticos, suas variações e relações foram substituídos, com backup local em artifacts/modelagem/definition-before. Parte dessas tabelas havia sido criada indevidamente para IDs convertidos em datas. Todas as tabelas de negócio originais foram mantidas. As colunas Column6…ColumnN sem cabeçalho na estrutura não eram usadas pelos visuais e foram retiradas da importação.

## Atualização e fontes

Executar scripts/prepare_workbook.py com o caminho do Excel original e depois atualizar no Desktop. O parâmetro Power Query pArquivoBase aponta para a cópia tratada local; em outra máquina, gerar a cópia e ajustar esse parâmetro. Excel não oferece query folding; seleção de colunas e tipos ocorre no Power Query.
