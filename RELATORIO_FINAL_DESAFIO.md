# Relatório Final — Análise FINBRA: Despesas por Função das Capitais Brasileiras

**Desafio Técnico — Estágio em Análise de Dados, Sefaz Maceió**

## Introdução

Este relatório analisa os dados de despesas por função das 26 capitais
brasileiras (Siconfi/FINBRA, Anexo I-E), com foco na comparação entre
valores **Empenhados** e **Pagos**, e um recorte especial para a
Prefeitura de Maceió.

**Período coberto**: 2020-2024 (26 capitais completas em todos os anos).
O ano de 2025 foi excluído das comparações entre anos por estar incompleto
(11 de 26 capitais reportadas até o momento da extração).

## Metodologia

- **ETL**: extração dos arquivos `.zip` do Siconfi, consolidação de todos
  os anos num único DataFrame (tratando encoding ISO-8859-1, separador
  `;`, decimal `,`), exportação para Parquet.
- **Indicadores**: Taxa de Execução (Pago/Empenhado) calculada excluindo
  agregados e subfunções (evita duplicar valor), com tratamento explícito
  de divisão por zero.
- **Testes**: todo o pipeline (ETL, indicadores, funções de análise) tem
  cobertura de testes unitários (`pytest`), seguindo TDD.
- Código-fonte completo em `codigo/`, testes em `testes/`, exploração
  interativa em `notebooks/analise.ipynb`.

## 1. Ranking Top 10 por ano — Educação, Saúde e Segurança Pública

Heatmap de posição no ranking de Taxa de Execução (Pago/Empenhado), restrito
às capitais que estiveram no top 10 em pelo menos um dos anos 2020-2024. A
posição real é mostrada em todos os anos, mesmo quando a capital caiu fora
do top 10, para deixar visível a movimentação no ranking.

![Top 10 — 12 - Educação](graficos/01_heatmap_educacao.svg)

![Top 10 — 10 - Saúde](graficos/01_heatmap_saude.svg)

![Top 10 — 06 - Segurança Pública](graficos/01_heatmap_seguranca.svg)

### Conclusão

Um dos maiores destaques da Prefeitura de Maceió foi com relação a funçãof Saúde, na qual esteve entre as 10 melhores capitais em termos de taxa de execução em todos os anos analisados, mantendo-se sempre entre as 4ª e 5ª posições.

Quanto a Educação, Maceió figurou no top 10 apenas nos anos de 2022 e 2023, ocupando a 8ª posição em ambos os períodos. Apesar de vir aumentando o seu posicionamento desde o ano de 2020, em 2024 houve uma ruptura, caindo da 8ª posição para a 24ª, sendo a sua pior marca dentre os anos analisados.

Em relação à Segurança Pública, a capital vinha mantendo bom posicionamento entre os anos de 2020 a 2022, embora tenha entrado entre as 10 melhores capitais em taxa de execução para a função apenas em 2021, ocupando a 5ª colocação. Assim como aconteceu com a educação, em 2023 e 2024 houve uma queda de posicionamento, ficando nas 24ª e 25ª posições respectivamente.

**Nota metodológica**: células vazias no heatmap significam que a capital
não tem nenhuma linha reportada para aquela função naquele ano no FINBRA —
não é erro de cálculo, é ausência do dado na fonte. Por exemplo, em
"06 - Segurança Pública": Porto Velho não reporta essa função em nenhum dos
5 anos (ausência estrutural), enquanto Teresina só falta especificamente em
2021 (buraco pontual, presente nos outros 4 anos).

## 2. Evolução histórica: Maceió vs. média das demais capitais

Taxa de Execução ano a ano (2020-2024), Maceió contra a média das outras
25 capitais. A faixa sombreada mostra o intervalo mínimo-máximo das demais,
para avaliar se Maceió está dentro da variação normal ou é um outlier.

![Evolução — 12 - Educação](graficos/02_evolucao_educacao.svg)

![Evolução — 10 - Saúde](graficos/02_evolucao_saude.svg)

![Evolução — 06 - Segurança Pública](graficos/02_evolucao_seguranca.svg)

### Conclusão

No contexto histórico, corroborando com a análise de posicionamento realizada acima, Maceió se destaca na função de Saúde, trabalhando com taxa de execução acima da média das demais capitais, superior a 95%. Dentre o período analisado, quase não houve variação na execução.

Quando passamos para a educação, o cenário não se repete. A capital em 2020 e 2021 se manteve abaixo da média das demais capitais, atingindo em 2021 a pior execução para a função analisada. Entretanto, o gráfico nos mostra que durante esse período, houve uma tendência de queda nas 26 capitais, o que pode estar relacionado aos impactos da pandemia de COVID-19 sobre a execução orçamentária, embora essa hipótese não possa ser confirmada apenas com os dados analisados. Apesar da retomada em 2022 e 2023, ficando acima da média, fechou 2024 em queda, chegando próximo a sua pior marca nesse recorte de tempo, contrariando a tendência de alta visualizada na média das demais capitais.

Em segurança pública a capital se mantinha acima da média dentre os anos de 2020 a 2022, tendo uma das melhores taxas de execução em 2021. Entretanto, houve uma queda abrupta em 2023, saindo de valores acima de 90% para abaixo de 60% de execução, contrariando mais uma vez os resultados obtidos pelas demais capitais. Apesar de uma leve retomada em 2024, ainda se manteve abaixo da média, apresentando-se fora da variação normalmente observada nas demais capitais.

**Nota metodológica**: em alguns anos a taxa de execução das "demais
capitais" pode passar de 100%. Isso ocorre porque "Despesas Pagas" num ano
pode incluir pagamento de Restos a Pagar de anos anteriores, enquanto
"Despesas Empenhadas" reflete só o empenho do ano corrente — um
descompasso de calendário contábil, não um erro de cálculo.

## 3. Melhor e pior função de Maceió, e se isso se replica nas demais

Cálculo feito sobre a **média 2020-2024** (não um ano isolado), para não
deixar uma oscilação pontual distorcer o resultado, com um **filtro de
materialidade**: só entram funções que representam ao menos 1% do
orçamento empenhado médio da capital — sem isso, uma função residual
poderia "vencer" apenas por ruído estatístico.

Em Maceió, no período 2020-2024:
- **Melhor execução**: 09 - Previdência Social (99.9%)
- **Pior execução**: 15 - Urbanismo (80.7%)

![Frequência melhor/pior função entre as capitais](graficos/03_frequencia_melhor_pior.svg)

A função mais comum como melhor execução entre as 26 capitais é
**09 - Previdência Social** (15 capitais), e como
pior execução é **15 - Urbanismo** (9 capitais).
O padrão de Maceió **replica** o padrão mais comum entre as capitais.

### Conclusão

Maceió tem a Previdência Social como a função com a melhor taxa de execução média nos anos analisados, quase 100%. Essa função se apresenta nesse mesmo cenário em 15 das 26 capitais. Esse resultado pode ser explicado devido à alta previsibilidade das despesas com previdência.

Já a função com a pior taxa de execução para a capital foi Urbanismo, com média de 80.7%, tendo incidência em 9 das 26 capitais analisadas. É possível que determinado padrão aconteça devido a complexidade das despesas, englobando obras que podem ter um prazo maior de conclusão.

## 4. Composição do orçamento empenhado por função (Maceió)

Gráfico de Pareto: barras mostram a participação percentual de cada função
no total empenhado em 2024; a linha mostra o percentual
acumulado.

![Composição por função](graficos/04_pareto_funcoes.svg)

**5 de 19 funções concentram 80% do orçamento
empenhado** de Maceió em 2024. As três maiores são
10 - Saúde (25.5%),
12 - Educação (15.8%) e
15 - Urbanismo (15.1%).

### Conclusão

Saúde, Educação e Urbanismo se apresentam como as funções com a maior porcentagem dos valores empenhados por Maceió em 2024. Considerando a importância, sobretudo da saúde e educação, sendo direitos fundamentais garantidos constitucionalmente, bem como a demanda da população por esses serviços, os seus posicionamentos são mais que naturais. 

## 5. Composição das subfunções de Saúde e Educação

Mesmo formato de Pareto, agora um nível mais fundo: dentro de Saúde e
Educação, para onde vai o dinheiro?

![Subfunções de Saúde e Educação](graficos/05_pareto_subfuncoes.svg)

Em Saúde, a subfunção com maior participação é
**10.302 - Assistência Hospitalar e Ambulatorial** (59.0%
do total da função). Em Educação, é
**12.361 - Ensino Fundamental** (37.6%
do total da função).

### Conclusão

Entre as subfunções da Saúde, a qual representa quase 30% do orçamento empenhado da capital de Maceió, a Assistência Hospitalar e Ambulatorial compõe 59%, sendo seguida pela Atenção Básica, com 27%. Juntas formam mais de 80% do empenho para a saúde.

Quanto à Educação, o Ensino Fundamental representa 37,6% do orçamento empenhado. A Educação Básica e o Ensino Infantil ocupam o terceiro e o quarto lugares, respectivamente, ficando abaixo apenas da Administração Geral.

## Conclusões gerais

Considerando as análises realizadas neste relatório, fica evidenciado o bom desempenho e a regularidade da Prefeitura de Maceió na execução dos empenhos voltados para a função de Saúde, mantendo valores próximos a 100% de execução e figurando em todos os anos entre as 5 melhores capitais neste quesito.

No que se refere a Educação, existe uma leve variação, cruzando a média das demais capitais em dois momentos. Entretanto, mesmo com números abaixo da média em 2020 e 2021, houve uma tendência nacional de queda, possivelmente um reflexo da pandemia de Covid-19. Em 2024, entretanto, após o aumento da sua execução nos anos anteriores, apresentou uma ruptura, caindo para números próximos dos de 2021.

A variação mais evidenciada, entretanto, considerando as funções analisadas, foi na Segurança Pública. Embora a capital tenha apresentado taxas de execução acima da média durante os períodos de 2020 a 2022, apresentou uma queda abrupta, partindo de valores acima de 90% para abaixo de 60%. Mesmo havendo uma leve retomada em 2024, ainda permaneceu abaixo da média e fora da variação normal visualizadas nas demais capitais.

## Limitações e trabalhos futuros

- **2025 incompleto**: excluído das comparações entre anos (ver Introdução).
- **Descompasso Empenhado/Pago entre exercícios**: pagamentos de Restos a
  Pagar de anos anteriores podem fazer a Taxa de Execução de um ano
  específico ultrapassar 100% (ver nota na Seção 2).
- **Filtro de materialidade (Seção 3)**: o limiar de 1% do orçamento é uma
  escolha metodológica; resultados podem mudar com um limiar diferente.
- **Não realizado por falta de tempo**: Taxa de Liquidação/Realização do
  Pagamento (decomposição do ciclo Empenho→Liquidação→Pagamento), CAGR do
  gasto per capita 2020-2024, e cruzamento aproximado com mínimos
  constitucionais (Saúde 15%, Educação 25% — o dataset não tem Receita
  Corrente Líquida, então seria uma aproximação, não o cálculo oficial).
