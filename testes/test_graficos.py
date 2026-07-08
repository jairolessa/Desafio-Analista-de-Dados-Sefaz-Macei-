import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

from src.graficos import (
    plotar_heatmap_top10,
    plotar_evolucao,
    plotar_pareto,
    plotar_frequencia_funcao,
)


def _df_execucao(linhas):
    return pd.DataFrame(
        linhas,
        columns=["Instituição", "Conta", "Coluna", "Valor", "ano", "tipo_conta"],
    )


class TestPlotarHeatmapTop10:
    def test_roda_sem_erro_e_retorna_axes_com_dado(self):
        linhas = []
        for i in range(1, 13):
            capital = f"Prefeitura Municipal de C{i} - XX"
            linhas.append((capital, "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"))
            linhas.append((capital, "10 - Saúde", "Despesas Pagas", 100 - i, 2020, "funcao"))
        df = _df_execucao(linhas)

        ax = plotar_heatmap_top10(df, conta="10 - Saúde", anos=[2020], top_n=10)

        assert ax is not None
        assert "Top 10" in ax.get_title()


class TestPlotarEvolucao:
    def test_roda_sem_erro_e_desenha_3_series(self):
        df = _df_execucao(
            [
                ("Maceió", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("Maceió", "10 - Saúde", "Despesas Pagas", 90, 2020, "funcao"),
                ("Salvador", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("Salvador", "10 - Saúde", "Despesas Pagas", 70, 2020, "funcao"),
            ]
        )

        ax = plotar_evolucao(df, conta="10 - Saúde", capital="Maceió", anos=[2020])

        # 2 linhas (Maceió, média das demais) + 1 fill_between (não conta como "line")
        assert len(ax.lines) == 2


class TestPlotarPareto:
    def test_desenha_barras_e_linha_acumulada(self):
        pareto_df = pd.DataFrame(
            {
                "Conta": ["10 - Saúde", "12 - Educação"],
                "valor": [300.0, 100.0],
                "percentual": [75.0, 25.0],
                "percentual_acumulado": [75.0, 100.0],
            }
        )

        ax = plotar_pareto(pareto_df, titulo="Teste")

        assert len(ax.patches) == 2  # 2 barras


class TestPlotarFrequenciaFuncao:
    def test_desenha_uma_barra_por_funcao(self):
        contagem = pd.Series({"09 - Previdência Social": 15, "01 - Legislativa": 3})

        ax = plotar_frequencia_funcao(contagem, titulo="Teste", cor="#4c72b0")

        assert len(ax.patches) == 2
