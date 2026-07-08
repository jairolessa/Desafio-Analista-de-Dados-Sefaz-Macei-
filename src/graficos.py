import matplotlib.pyplot as plt
import seaborn as sns

from src.analises import matriz_posicoes, evolucao_execucao_vs_demais
from src.estilo_graficos import (
    nome_curto,
    COR_DESTAQUE,
    COR_BASE,
    COR_FAIXA,
    COR_LINHA_ACUMULADA,
)


def plotar_heatmap_top10(df, conta, anos, top_n=10, ax=None):
    
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 6))

    matriz = matriz_posicoes(df, conta=conta, anos=anos, top_n=top_n)
    matriz.index = [nome_curto(i) for i in matriz.index]
    matriz = matriz.sort_values(anos[-1])

    sns.heatmap(
        matriz,
        annot=True,
        fmt=".0f",
        cmap="RdYlGn_r",
        center=top_n,
        linewidths=0.5,
        cbar_kws={"label": "Posição no ranking"},
        ax=ax,
    )
    ax.set_title(f"Top {top_n} — {conta}")
    ax.set_xlabel("Ano")
    ax.set_ylabel("")
    return ax


def plotar_evolucao(df, conta, capital, anos, ax=None):
    
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 5))

    evo = evolucao_execucao_vs_demais(df, conta=conta, capital=capital, anos=anos)

    ax.fill_between(
        evo["ano"],
        evo["min_demais"] * 100,
        evo["max_demais"] * 100,
        color=COR_FAIXA,
        alpha=0.6,
        label="Variação das demais (mín-máx)",
    )
    ax.plot(
        evo["ano"], evo["media_demais"] * 100, color=COR_BASE, marker="o",
        label="Média das demais",
    )
    ax.plot(
        evo["ano"], evo["capital"] * 100, color=COR_DESTAQUE, marker="o",
        linewidth=2.5, label=capital,
    )

    ax.set_xticks(evo["ano"])
    ax.set_ylabel("Taxa de Execução (%)")
    ax.set_title(conta)

    ultimo = evo.iloc[-1]
    ax.annotate(
        f"{ultimo['capital']:.1%}",
        xy=(ultimo["ano"], ultimo["capital"] * 100),
        xytext=(6, 6),
        textcoords="offset points",
        fontsize=9,
        color=COR_DESTAQUE,
        fontweight="bold",
    )
    return ax


def plotar_pareto(pareto_df, titulo, ax=None):
    
    if ax is None:
        _, ax = plt.subplots(figsize=(11, 6))

    ax.bar(range(len(pareto_df)), pareto_df["percentual"], color=COR_BASE)
    ax.set_xticks(range(len(pareto_df)))
    ax.set_xticklabels(pareto_df["Conta"], rotation=75, ha="right", fontsize=8)
    ax.set_ylabel("% do total empenhado")

    n_anotar = min(5, len(pareto_df))
    for i in range(n_anotar):
        valor = pareto_df.iloc[i]["percentual"]
        ax.text(i, valor + 0.5, f"{valor:.1f}%", ha="center", fontsize=7.5, color=COR_BASE)

    eixo_acumulado = ax.twinx()
    eixo_acumulado.plot(
        range(len(pareto_df)), pareto_df["percentual_acumulado"],
        color=COR_LINHA_ACUMULADA, marker="o", markersize=3,
    )
    eixo_acumulado.set_ylabel("% acumulado", color=COR_LINHA_ACUMULADA)
    eixo_acumulado.set_ylim(0, 105)
    eixo_acumulado.axhline(80, color=COR_LINHA_ACUMULADA, linestyle=":", linewidth=1)
    eixo_acumulado.grid(False)

    ax.set_title(titulo)
    return ax


def plotar_frequencia_funcao(contagem, titulo, cor, ax=None):
    
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))

    ax.barh(contagem.index[::-1], contagem.values[::-1], color=cor)
    ax.set_title(titulo)
    ax.set_xlabel("Nº de capitais")

    for i, valor in enumerate(contagem.values[::-1]):
        ax.text(valor + 0.2, i, str(valor), va="center", fontsize=9)
    return ax
