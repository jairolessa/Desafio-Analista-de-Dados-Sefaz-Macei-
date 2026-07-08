import re

import matplotlib.pyplot as plt

COR_DESTAQUE = "#e07b39"
COR_BASE = "#4c72b0"
COR_FAIXA = "#c8d4e8"
COR_LINHA_ACUMULADA = "#c44e52"
COR_TEXTO = "#333333"
COR_GRID = "#dddddd"


def aplicar_estilo() -> None:
    
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.edgecolor": COR_GRID,
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.color": COR_GRID,
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "text.color": COR_TEXTO,
            "axes.labelcolor": COR_TEXTO,
            "xtick.color": COR_TEXTO,
            "ytick.color": COR_TEXTO,
        }
    )


def nome_curto(instituicao: str) -> str:
    
    sem_prefixo = re.sub(r"^Prefeitura Municipal d[eo] ", "", instituicao)
    return sem_prefixo.replace(" - ", "/")


def cores_destacando(instituicoes, capital: str = "Maceió") -> list:
    
    return [COR_DESTAQUE if capital in inst else COR_BASE for inst in instituicoes]


def salvar_figura(fig, caminho) -> None:
    
    fig.savefig(caminho, format="svg", bbox_inches="tight")


def adicionar_fonte(fig, texto: str = "Fonte: FINBRA/Siconfi (2020-2024). Elaboração própria.") -> None:
    
    fig.text(0.99, -0.02, texto, ha="right", va="top", fontsize=8, color="#888888", style="italic")
