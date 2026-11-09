# Dicionário de dados — inspeção real

Perfil das abas da planilha original do desafio (BaseDados.xlsx), da qual deriva `data/processed/BaseDados_Tratada.xlsx`. As tabelas nomeadas auxiliares `Table_1`…`Table_8` existem na planilha original, mas não são carregadas no modelo.


Base original preservada. Base tratada é derivada, não uma segunda fonte a somar. Valores são mensais, não notas fiscais, vendas individuais ou lançamentos bancários.

## dEstruturaDRE
Finalidade: estrutura gerencial por filial. Linhas de negócio: 39. Linhas vazias excluídas: 960.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| id | str → texto | 0 | 39 |
| index | float → inteiro | 0 | 13 |
| contaGerencial | str → texto | 0 | 13 |
| subtotal | float → inteiro | 0 | 2 |
| empresa | str → texto | 0 | 3 |

Chave/grão: id. Duplicidades: 0.

## dPlanoConta
Finalidade: cadastro/classificação das contas por filial. Linhas de negócio: 129. Linhas vazias excluídas: 200.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| id | str → texto | 0 | 129 |
| index | float → inteiro | 0 | 43 |
| descricaoN1 | str → texto | 0 | 17 |
| descricaoN2 | str → texto | 0 | 43 |
| detalharN2 | float → inteiro | 0 | 2 |
| mascaraDRE_id | str → texto | 0 | 24 |
| tipoLancamento | float → inteiro | 0 | 2 |

Chave/grão: id. Duplicidades: 0.
FK mascaraDRE_id → dEstruturaDRE.id. tipoLancamento determina natureza +1/-1.
Tabela Excel nomeada auxiliar `Table_1`: intervalo A1:C130; recorte desta aba, não nova fonte de fatos.
Tabela Excel nomeada auxiliar `Table_2`: intervalo D2:D6; recorte desta aba, não nova fonte de fatos.
Tabela Excel nomeada auxiliar `Table_3`: intervalo D11:D12; recorte desta aba, não nova fonte de fatos.
Tabela Excel nomeada auxiliar `Table_4`: intervalo D39:D49; recorte desta aba, não nova fonte de fatos.
Tabela Excel nomeada auxiliar `Table_5`: intervalo D54:D55; recorte desta aba, não nova fonte de fatos.
Tabela Excel nomeada auxiliar `Table_6`: intervalo D82:D92; recorte desta aba, não nova fonte de fatos.
Tabela Excel nomeada auxiliar `Table_7`: intervalo D97:D98; recorte desta aba, não nova fonte de fatos.
Tabela Excel nomeada auxiliar `Table_8`: intervalo D125:D130; recorte desta aba, não nova fonte de fatos.

## fOrcamento
Finalidade: orçamento mensal. Linhas de negócio: 4644. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 36 |
| planoContas_id | str → texto | 0 | 129 |
| valor | float → decimal | 0 | 4628 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2021 a 01/12/2023. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fPrevisao
Finalidade: previsão mensal. Linhas de negócio: 4644. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 36 |
| planoContas_id | str → texto | 0 | 129 |
| valor | float → decimal | 0 | 4509 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2021 a 01/12/2023. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento1_ano1
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 516. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 12 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 334 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2021 a 01/12/2021. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento2_ano1
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 516. Linhas vazias excluídas: 483.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 12 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 335 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2021 a 01/12/2021. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento3_ano1
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 516. Linhas vazias excluídas: 483.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 12 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 337 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2021 a 01/12/2021. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento1_ano2
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 516. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 12 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 378 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2022 a 01/12/2022. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento2_ano2
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 516. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 12 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 439 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2022 a 01/12/2022. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento3_ano2
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 516. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 12 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 439 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2022 a 01/12/2022. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento1_ano3
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 215. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 5 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 189 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2023 a 01/05/2023. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento2_ano3
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 215. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 5 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 185 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2023 a 01/05/2023. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## fLancamento3_ano3
Finalidade: realizado mensal por conta; fragmento de filial/ano. Linhas de negócio: 215. Linhas vazias excluídas: 0.

| Coluna | Tipo observado → modelo | Nulos | Distintos não nulos |
|---|---|---:|---:|
| competencia_data | datetime → data | 0 | 5 |
| planoContas_id | str → texto | 0 | 43 |
| valor | float → decimal | 0 | 187 |

Chave/grão: competencia_data + planoContas_id. Duplicidades: 0.
Período: 01/01/2023 a 01/05/2023. FK planoContas_id → dPlanoConta.id; competência → dCalendario.Data; filial_id derivada do prefixo e validada no cadastro → dFilial.id.

## Tabelas derivadas e de apresentação
- fLancamentos: união das nove fontes de realizado; 3.741 registros, grão mensal/conta. Não somar suas origens novamente.
- dFilial: 3 chaves textuais, nomes obtidos de empresa da estrutura: 01 São Paulo, 02 Rio de Janeiro, 03 Florianópolis.
- dCalendario: 1.095 dias, 2021–2023; Data única, Ano/MesNum/AnoMesINT inteiros, nomes textuais pt-BR e atributos de ordenação. Sem FK; dimensão no lado 1.
- dDRE: linhas de apresentação, desconectada; medidas selecionam os grupos originais, sem somar linhas calculadas.
- dPeriodo: seletor desconectado de contexto, YTD e ano completo; utilizado apenas pelas medidas da matriz.

## Qualidade e classificação
- Movimentos sem classificação: 0. Contas sem máscara: zero. Sinais da natureza do plano: somente -1 e +1.
- Valores brutos negativos: {'Realizado': 18, 'Previsto': 20, 'Orcado': 20}. Preservados e multiplicados pela natureza; não aplicar ABS aos movimentos.
- As 15 descrições vazias de dEstruturaDRE são subtotais marcados por subtotal=1. Seus rótulos gerenciais são explicitados nas regras; não representam contas desconhecidas.
- Na importação anterior, códigos haviam virado datas e linhas vazias eram carregadas. A base tratada corrige esses problemas.
