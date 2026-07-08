import pandas as pd
import pytest

from src.analises import (
    rankear_taxa_execucao,
    matriz_posicoes,
    evolucao_execucao_vs_demais,
    taxa_execucao_media_periodo,
    melhor_e_pior_funcao,
    composicao_pareto,
)


def _df_execucao(linhas):
    
    return pd.DataFrame(
        linhas,
        columns=["Instituição", "Conta", "Coluna", "Valor", "ano", "tipo_conta"],
    )


class TestRankearTaxaExecucao:
    def test_ordena_desc_e_atribui_posicao_1_indexada(self):
        df = _df_execucao(
            [
                ("A", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("A", "10 - Saúde", "Despesas Pagas", 50, 2020, "funcao"),
                ("B", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("B", "10 - Saúde", "Despesas Pagas", 90, 2020, "funcao"),
            ]
        )

        resultado = rankear_taxa_execucao(df, conta="10 - Saúde", ano=2020)

        assert list(resultado["Instituição"]) == ["B", "A"]
        assert list(resultado["posicao"]) == [1, 2]

    def test_filtra_pela_conta_e_ano_pedidos(self):
        df = _df_execucao(
            [
                ("A", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("A", "10 - Saúde", "Despesas Pagas", 90, 2020, "funcao"),
                ("A", "12 - Educação", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("A", "12 - Educação", "Despesas Pagas", 10, 2020, "funcao"),
                ("A", "10 - Saúde", "Despesas Empenhadas", 100, 2021, "funcao"),
                ("A", "10 - Saúde", "Despesas Pagas", 5, 2021, "funcao"),
            ]
        )

        resultado = rankear_taxa_execucao(df, conta="10 - Saúde", ano=2020)

        assert len(resultado) == 1
        assert resultado.iloc[0]["taxa_execucao"] == pytest.approx(0.9)


class TestMatrizPosicoes:
    def test_inclui_apenas_capitais_que_entraram_no_top_n_em_algum_ano(self):
        linhas = []
        
        for i in range(1, 13):
            capital = f"C{i}"
            empenhado = 100
            pago = 100 - i
            linhas.append((capital, "10 - Saúde", "Despesas Empenhadas", empenhado, 2020, "funcao"))
            linhas.append((capital, "10 - Saúde", "Despesas Pagas", pago, 2020, "funcao"))
        df = _df_execucao(linhas)

        matriz = matriz_posicoes(df, conta="10 - Saúde", anos=[2020], top_n=10)

        assert "C11" not in matriz.index
        assert "C12" not in matriz.index
        assert "C1" in matriz.index
        assert len(matriz) == 10

    def test_mostra_posicao_real_mesmo_fora_do_top_n_em_outro_ano(self):
        linhas = []
        for ano, ordem in [(2020, list(range(1, 13))), (2021, list(range(12, 0, -1)))]:
            for posicao_desejada, i in enumerate(ordem, start=1):
                capital = f"C{i}"
                pago = 100 - posicao_desejada
                linhas.append((capital, "10 - Saúde", "Despesas Empenhadas", 100, ano, "funcao"))
                linhas.append((capital, "10 - Saúde", "Despesas Pagas", pago, ano, "funcao"))
        df = _df_execucao(linhas)

        matriz = matriz_posicoes(df, conta="10 - Saúde", anos=[2020, 2021], top_n=10)

        assert "C12" in matriz.index
        assert pd.notna(matriz.loc["C12", 2020])


class TestEvolucaoExecucaoVsDemais:
    def test_separa_capital_de_interesse_das_demais(self):
        df = _df_execucao(
            [
                ("Maceió", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("Maceió", "10 - Saúde", "Despesas Pagas", 90, 2020, "funcao"),
                ("Salvador", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("Salvador", "10 - Saúde", "Despesas Pagas", 50, 2020, "funcao"),
                ("Recife", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("Recife", "10 - Saúde", "Despesas Pagas", 70, 2020, "funcao"),
            ]
        )

        resultado = evolucao_execucao_vs_demais(
            df, conta="10 - Saúde", capital="Maceió", anos=[2020]
        )

        linha = resultado.iloc[0]
        assert linha["capital"] == pytest.approx(0.9)
        assert linha["media_demais"] == pytest.approx(0.6)
        assert linha["min_demais"] == pytest.approx(0.5)
        assert linha["max_demais"] == pytest.approx(0.7)

    def test_um_ano_por_linha(self):
        linhas = []
        for ano, taxa_maceio, taxa_outra in [(2020, 0.9, 0.5), (2021, 0.8, 0.6)]:
            linhas.append(("Maceió", "10 - Saúde", "Despesas Empenhadas", 100, ano, "funcao"))
            linhas.append(("Maceió", "10 - Saúde", "Despesas Pagas", taxa_maceio * 100, ano, "funcao"))
            linhas.append(("Salvador", "10 - Saúde", "Despesas Empenhadas", 100, ano, "funcao"))
            linhas.append(("Salvador", "10 - Saúde", "Despesas Pagas", taxa_outra * 100, ano, "funcao"))
        df = _df_execucao(linhas)

        resultado = evolucao_execucao_vs_demais(
            df, conta="10 - Saúde", capital="Maceió", anos=[2020, 2021]
        )

        assert list(resultado["ano"]) == [2020, 2021]


class TestTaxaExecucaoMediaPeriodo:
    def test_calcula_media_ao_longo_dos_anos(self):
        df = _df_execucao(
            [
                ("Maceió", "10 - Saúde", "Despesas Empenhadas", 100, 2020, "funcao"),
                ("Maceió", "10 - Saúde", "Despesas Pagas", 100, 2020, "funcao"),
                ("Maceió", "10 - Saúde", "Despesas Empenhadas", 100, 2021, "funcao"),
                ("Maceió", "10 - Saúde", "Despesas Pagas", 50, 2021, "funcao"),
            ]
        )

        resultado = taxa_execucao_media_periodo(df, anos=[2020, 2021])

        linha = resultado[
            (resultado["Instituição"] == "Maceió") & (resultado["Conta"] == "10 - Saúde")
        ].iloc[0]
        assert linha["taxa_execucao_media"] == pytest.approx(0.75)
        assert linha["empenhado_medio"] == pytest.approx(100.0)


class TestMelhorEPiorFuncao:
    def test_identifica_melhor_e_pior_respeitando_materialidade(self):
        resumo = pd.DataFrame(
            {
                "Instituição": ["Maceió", "Maceió", "Maceió"],
                "Conta": ["10 - Saúde", "12 - Educação", "01 - Legislativa"],
                "taxa_execucao_media": [0.9, 0.5, 0.99],
                "empenhado_medio": [500_000, 500_000, 1_000],
            }
        )

        resultado = melhor_e_pior_funcao(resumo, limiar_participacao=0.01)

        linha = resultado.iloc[0]
        assert linha["melhor_funcao"] == "10 - Saúde"
        assert linha["pior_funcao"] == "12 - Educação"

    def test_uma_linha_por_instituicao(self):
        resumo = pd.DataFrame(
            {
                "Instituição": ["Maceió", "Maceió", "Salvador", "Salvador"],
                "Conta": ["10 - Saúde", "12 - Educação"] * 2,
                "taxa_execucao_media": [0.9, 0.5, 0.8, 0.6],
                "empenhado_medio": [500_000, 500_000, 500_000, 500_000],
            }
        )

        resultado = melhor_e_pior_funcao(resumo, limiar_participacao=0.01)

        assert len(resultado) == 2
        assert set(resultado["Instituição"]) == {"Maceió", "Salvador"}


class TestComposicaoPareto:
    def test_ordena_desc_e_calcula_percentual_acumulado(self):
        df = _df_execucao(
            [
                ("Maceió", "10 - Saúde", "Despesas Empenhadas", 300, 2024, "funcao"),
                ("Maceió", "12 - Educação", "Despesas Empenhadas", 100, 2024, "funcao"),
            ]
        )

        resultado = composicao_pareto(df, capital="Maceió", ano=2024, nivel="funcao")

        assert list(resultado["Conta"]) == ["10 - Saúde", "12 - Educação"]
        assert resultado.iloc[0]["percentual"] == pytest.approx(75.0)
        assert resultado.iloc[-1]["percentual_acumulado"] == pytest.approx(100.0)

    def test_filtra_subfuncao_por_prefixo_da_conta_pai(self):
        df = _df_execucao(
            [
                ("Maceió", "10.301 - Atenção Básica", "Despesas Empenhadas", 200, 2024, "subfuncao"),
                ("Maceió", "12.361 - Ensino Fundamental", "Despesas Empenhadas", 300, 2024, "subfuncao"),
            ]
        )

        resultado = composicao_pareto(
            df, capital="Maceió", ano=2024, nivel="subfuncao", filtro_conta="10"
        )

        assert len(resultado) == 1
        assert resultado.iloc[0]["Conta"] == "10.301 - Atenção Básica"

    def test_usa_apenas_despesas_empenhadas(self):
        df = _df_execucao(
            [
                ("Maceió", "10 - Saúde", "Despesas Empenhadas", 100, 2024, "funcao"),
                ("Maceió", "10 - Saúde", "Despesas Pagas", 999, 2024, "funcao"),
            ]
        )

        resultado = composicao_pareto(df, capital="Maceió", ano=2024, nivel="funcao")

        assert resultado.iloc[0]["valor"] == pytest.approx(100.0)
