import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.analises import (
    taxa_execucao_media_periodo,
    melhor_e_pior_funcao,
    composicao_pareto,
)
from src.estilo_graficos import aplicar_estilo, salvar_figura, adicionar_fonte, COR_BASE
from src.graficos import (
    plotar_heatmap_top10,
    plotar_evolucao,
    plotar_pareto,
    plotar_frequencia_funcao,
)

RAIZ = Path(__file__).resolve().parent
CAMINHO_PARQUET = RAIZ / "dados_consolidados" / "finbra_consolidado.parquet"
DIR_RELATORIO = RAIZ / "relatorio"
DIR_GRAFICOS = DIR_RELATORIO / "graficos"

CAPITAL = "Maceió"
ANOS_COMPLETOS = [2020, 2021, 2022, 2023, 2024]
ANO_COMPOSICAO = 2024
FUNCOES_INTERESSE = [
    ("12 - Educação", "educacao"),
    ("10 - Saúde", "saude"),
    ("06 - Segurança Pública", "seguranca"),
]


def salvar(fig, nome_arquivo: str) -> str:
    """Adiciona a nota de fonte, salva em SVG e devolve o caminho relativo
    (pro markdown referenciar) já formatado como link de imagem."""
    adicionar_fonte(fig)
    caminho = DIR_GRAFICOS / nome_arquivo
    salvar_figura(fig, caminho)
    plt.close(fig)
    return f"graficos/{nome_arquivo}"


def gerar_secao_1(df: pd.DataFrame) -> str:
    imagens = []
    for conta, slug in FUNCOES_INTERESSE:
        fig, ax = plt.subplots(figsize=(7, 6))
        plotar_heatmap_top10(df, conta=conta, anos=ANOS_COMPLETOS, top_n=10, ax=ax)
        imagens.append(salvar(fig, f"01_heatmap_{slug}.svg"))

    corpo = "\n\n".join(f"![Top 10 — {c}]({img})" for (c, _), img in zip(FUNCOES_INTERESSE, imagens))
    return f"""## 1. Ranking Top 10 por ano — Educação, Saúde e Segurança Pública

Heatmap de posição no ranking de Taxa de Execução (Pago/Empenhado), restrito
às capitais que estiveram no top 10 em pelo menos um dos anos 2020-2024. A
posição real é mostrada em todos os anos, mesmo quando a capital caiu fora
do top 10, para deixar visível a movimentação no ranking.

{corpo}

### Conclusão



**Nota metodológica**: células vazias no heatmap significam que a capital
não tem nenhuma linha reportada para aquela função naquele ano no FINBRA —
não é erro de cálculo, é ausência do dado na fonte. Por exemplo, em
"06 - Segurança Pública": Porto Velho não reporta essa função em nenhum dos
5 anos (ausência estrutural), enquanto Teresina só falta especificamente em
2021 (buraco pontual, presente nos outros 4 anos).
"""


def gerar_secao_2(df: pd.DataFrame) -> str:
    imagens = []
    for conta, slug in FUNCOES_INTERESSE:
        fig, ax = plt.subplots(figsize=(9, 5))
        plotar_evolucao(df, conta=conta, capital=CAPITAL, anos=ANOS_COMPLETOS, ax=ax)
        ax.legend(loc="lower left", fontsize=9)
        imagens.append(salvar(fig, f"02_evolucao_{slug}.svg"))

    corpo = "\n\n".join(f"![Evolução — {c}]({img})" for (c, _), img in zip(FUNCOES_INTERESSE, imagens))
    return f"""## 2. Evolução histórica: {CAPITAL} vs. média das demais capitais

Taxa de Execução ano a ano (2020-2024), {CAPITAL} contra a média das outras
25 capitais. A faixa sombreada mostra o intervalo mínimo-máximo das demais,
para avaliar se {CAPITAL} está dentro da variação normal ou é um outlier.

{corpo}

### Conclusão



**Nota metodológica**: em alguns anos a taxa de execução das "demais
capitais" pode passar de 100%. Isso ocorre porque "Despesas Pagas" num ano
pode incluir pagamento de Restos a Pagar de anos anteriores, enquanto
"Despesas Empenhadas" reflete só o empenho do ano corrente — um
descompasso de calendário contábil, não um erro de cálculo.
"""


def gerar_secao_3(df: pd.DataFrame) -> str:
    resumo = taxa_execucao_media_periodo(df, anos=ANOS_COMPLETOS)
    melhor_pior = melhor_e_pior_funcao(resumo, limiar_participacao=0.01)
    linha_capital = melhor_pior[melhor_pior["Instituição"].str.contains(CAPITAL)].iloc[0]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    contagem_melhor = melhor_pior["melhor_funcao"].value_counts().head(8)
    plotar_frequencia_funcao(
        contagem_melhor, "Função mais comum como MELHOR execução\n(entre as 26 capitais)",
        COR_BASE, ax=axes[0],
    )
    contagem_pior = melhor_pior["pior_funcao"].value_counts().head(8)
    plotar_frequencia_funcao(
        contagem_pior, "Função mais comum como PIOR execução\n(entre as 26 capitais)",
        "#c44e52", ax=axes[1],
    )
    imagem = salvar(fig, "03_frequencia_melhor_pior.svg")

    replica_melhor = contagem_melhor.index[0] == linha_capital["melhor_funcao"]
    replica_pior = contagem_pior.index[0] == linha_capital["pior_funcao"]

    return f"""## 3. Melhor e pior função de {CAPITAL}, e se isso se replica nas demais

Cálculo feito sobre a **média 2020-2024** (não um ano isolado), para não
deixar uma oscilação pontual distorcer o resultado, com um **filtro de
materialidade**: só entram funções que representam ao menos 1% do
orçamento empenhado médio da capital — sem isso, uma função residual
poderia "vencer" apenas por ruído estatístico.

Em {CAPITAL}, no período 2020-2024:
- **Melhor execução**: {linha_capital['melhor_funcao']} ({linha_capital['melhor_taxa']:.1%})
- **Pior execução**: {linha_capital['pior_funcao']} ({linha_capital['pior_taxa']:.1%})

![Frequência melhor/pior função entre as capitais]({imagem})

A função mais comum como melhor execução entre as 26 capitais é
**{contagem_melhor.index[0]}** ({contagem_melhor.iloc[0]} capitais), e como
pior execução é **{contagem_pior.index[0]}** ({contagem_pior.iloc[0]} capitais).
{"O padrão de " + CAPITAL + " **replica** o padrão mais comum entre as capitais." if replica_melhor and replica_pior else "O padrão de " + CAPITAL + " diverge, ao menos parcialmente, do padrão mais comum entre as capitais."}

### Conclusão


"""


def gerar_secao_4(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    pareto_funcoes = composicao_pareto(df, capital=CAPITAL, ano=ANO_COMPOSICAO, nivel="funcao")

    fig, ax = plt.subplots(figsize=(11, 6))
    plotar_pareto(
        pareto_funcoes, f"Composição do Empenhado por Função — {CAPITAL} ({ANO_COMPOSICAO})", ax=ax
    )
    imagem = salvar(fig, "04_pareto_funcoes.svg")

    n_80 = (pareto_funcoes["percentual_acumulado"] <= 80).sum() + 1

    texto = f"""## 4. Composição do orçamento empenhado por função ({CAPITAL})

Gráfico de Pareto: barras mostram a participação percentual de cada função
no total empenhado em {ANO_COMPOSICAO}; a linha mostra o percentual
acumulado.

![Composição por função]({imagem})

**{n_80} de {len(pareto_funcoes)} funções concentram 80% do orçamento
empenhado** de {CAPITAL} em {ANO_COMPOSICAO}. As três maiores são
{pareto_funcoes.iloc[0]['Conta']} ({pareto_funcoes.iloc[0]['percentual']:.1f}%),
{pareto_funcoes.iloc[1]['Conta']} ({pareto_funcoes.iloc[1]['percentual']:.1f}%) e
{pareto_funcoes.iloc[2]['Conta']} ({pareto_funcoes.iloc[2]['percentual']:.1f}%).

### Conclusão


"""
    return texto, pareto_funcoes


def gerar_secao_5(df: pd.DataFrame) -> str:
    pareto_saude = composicao_pareto(
        df, capital=CAPITAL, ano=ANO_COMPOSICAO, nivel="subfuncao", filtro_conta="10"
    )
    pareto_educacao = composicao_pareto(
        df, capital=CAPITAL, ano=ANO_COMPOSICAO, nivel="subfuncao", filtro_conta="12"
    )

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    plotar_pareto(pareto_saude, f"Subfunções de Saúde — {CAPITAL} ({ANO_COMPOSICAO})", ax=axes[0])
    plotar_pareto(pareto_educacao, f"Subfunções de Educação — {CAPITAL} ({ANO_COMPOSICAO})", ax=axes[1])
    imagem = salvar(fig, "05_pareto_subfuncoes.svg")

    return f"""## 5. Composição das subfunções de Saúde e Educação

Mesmo formato de Pareto, agora um nível mais fundo: dentro de Saúde e
Educação, para onde vai o dinheiro?

![Subfunções de Saúde e Educação]({imagem})

Em Saúde, a subfunção com maior participação é
**{pareto_saude.iloc[0]['Conta']}** ({pareto_saude.iloc[0]['percentual']:.1f}%
do total da função). Em Educação, é
**{pareto_educacao.iloc[0]['Conta']}** ({pareto_educacao.iloc[0]['percentual']:.1f}%
do total da função).

### Conclusão


"""


def main() -> None:
    aplicar_estilo()
    DIR_GRAFICOS.mkdir(parents=True, exist_ok=True)

    if not CAMINHO_PARQUET.exists():
        print(f"Parquet não encontrado em {CAMINHO_PARQUET}. Rode main.py primeiro.")
        sys.exit(1)

    df = pd.read_parquet(CAMINHO_PARQUET)
    df_completo = df[df["ano"] != 2025].copy()

    n_capitais_2025 = df[df["ano"] == 2025]["Instituição"].nunique()

    secoes = [
        gerar_secao_1(df_completo),
        gerar_secao_2(df_completo),
        gerar_secao_3(df_completo),
    ]
    secao_4, pareto_funcoes = gerar_secao_4(df_completo)
    secoes.append(secao_4)
    secoes.append(gerar_secao_5(df_completo))

    cabecalho = f"""# Relatório Final — Análise FINBRA: Despesas por Função das Capitais Brasileiras

**Desafio Técnico — Estágio em Análise de Dados, Sefaz Maceió**

## Introdução

Este relatório analisa os dados de despesas por função das 26 capitais
brasileiras (Siconfi/FINBRA, Anexo I-E), com foco na comparação entre
valores **Empenhados** e **Pagos**, e um recorte especial para a
Prefeitura de {CAPITAL}.

**Período coberto**: 2020-2024 (26 capitais completas em todos os anos).
O ano de 2025 foi excluído das comparações entre anos por estar incompleto
({n_capitais_2025} de 26 capitais reportadas até o momento da extração).

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

"""

    rodape = """## Conclusões gerais



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
""".replace("{capital}", CAPITAL)

    conteudo_final = cabecalho + "\n".join(secoes) + "\n" + rodape

    caminho_md = DIR_RELATORIO / "relatorio_final.md"
    caminho_md.write_text(conteudo_final, encoding="utf-8")
    print(f"Relatório gerado em {caminho_md}")
    print(f"Gráficos salvos em {DIR_GRAFICOS}")


if __name__ == "__main__":
    main()
