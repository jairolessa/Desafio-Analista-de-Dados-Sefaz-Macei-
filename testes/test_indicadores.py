import pandas as pd
import pytest

from src.indicadores import taxa_execucao, gasto_per_capita


class TestTaxaExecucao:

    def test_calcula_taxa_basica(self):
        df = pd.DataFrame(
            {
                "Instituição": ["Maceió"] * 2,
                "Conta": ["10 - Saúde"] * 2,
                "Coluna": ["Despesas Empenhadas", "Despesas Pagas"],
                "Valor": [100.0, 80.0],
                "ano": [2020, 2020],
                "tipo_conta": ["funcao", "funcao"],
            }
        )

        resultado = taxa_execucao(df)

        linha = resultado.iloc[0]
        assert linha["empenhado"] == pytest.approx(100.0)
        assert linha["pago"] == pytest.approx(80.0)
        assert linha["taxa_execucao"] == pytest.approx(0.8)

    def test_ignora_subfuncoes_e_agregados_para_nao_duplicar_valor(self):
    
        df = pd.DataFrame(
            {
                "Instituição": ["Maceió"] * 4,
                "Conta": [
                    "10 - Saúde",
                    "10 - Saúde",
                    "10.301 - Atenção Básica",
                    "Despesas Exceto Intraorçamentárias",
                ],
                "Coluna": [
                    "Despesas Empenhadas",
                    "Despesas Pagas",
                    "Despesas Empenhadas",
                    "Despesas Empenhadas",
                ],
                "Valor": [100.0, 80.0, 999_999.0, 999_999.0],
                "ano": [2020] * 4,
                "tipo_conta": ["funcao", "funcao", "subfuncao", "agregado"],
            }
        )

        resultado = taxa_execucao(df)

        assert len(resultado) == 1
        assert resultado.iloc[0]["empenhado"] == pytest.approx(100.0)

    def test_divisao_por_zero_retorna_nan_em_vez_de_erro_ou_infinito(self):
        
        df = pd.DataFrame(
            {
                "Instituição": ["Maceió"],
                "Conta": ["10 - Saúde"],
                "Coluna": ["Despesas Pagas"],
                "Valor": [50.0],
                "ano": [2020],
                "tipo_conta": ["funcao"],
            }
        )

        resultado = taxa_execucao(df)

        assert resultado.iloc[0]["empenhado"] == 0.0
        assert pd.isna(resultado.iloc[0]["taxa_execucao"])

    def test_agrupa_capitais_separadamente(self):
        df = pd.DataFrame(
            {
                "Instituição": ["Maceió", "Maceió", "Salvador", "Salvador"],
                "Conta": ["10 - Saúde"] * 4,
                "Coluna": ["Despesas Empenhadas", "Despesas Pagas"] * 2,
                "Valor": [100.0, 90.0, 200.0, 100.0],
                "ano": [2020] * 4,
                "tipo_conta": ["funcao"] * 4,
            }
        )

        resultado = taxa_execucao(df)

        assert len(resultado) == 2
        maceio = resultado[resultado["Instituição"] == "Maceió"].iloc[0]
        salvador = resultado[resultado["Instituição"] == "Salvador"].iloc[0]
        assert maceio["taxa_execucao"] == pytest.approx(0.9)
        assert salvador["taxa_execucao"] == pytest.approx(0.5)

    def test_agrupa_anos_separadamente(self):
        df = pd.DataFrame(
            {
                "Instituição": ["Maceió"] * 4,
                "Conta": ["10 - Saúde"] * 4,
                "Coluna": ["Despesas Empenhadas", "Despesas Pagas"] * 2,
                "Valor": [100.0, 100.0, 200.0, 50.0],
                "ano": [2020, 2020, 2021, 2021],
                "tipo_conta": ["funcao"] * 4,
            }
        )

        resultado = taxa_execucao(df)

        assert len(resultado) == 2
        taxa_2020 = resultado[resultado["ano"] == 2020].iloc[0]["taxa_execucao"]
        taxa_2021 = resultado[resultado["ano"] == 2021].iloc[0]["taxa_execucao"]
        assert taxa_2020 == pytest.approx(1.0)
        assert taxa_2021 == pytest.approx(0.25)


class TestGastoPerCapita:
    def test_calcula_valor_dividido_pela_populacao(self):
        df = pd.DataFrame({"Instituição": ["Maceió"], "Valor": [1_000_000.0], "População": [1_000_000]})

        resultado = gasto_per_capita(df)

        assert resultado.iloc[0]["valor_per_capita"] == pytest.approx(1.0)

    def test_preserva_colunas_originais(self):
        df = pd.DataFrame(
            {"Instituição": ["Maceió"], "Valor": [500.0], "População": [100], "ano": [2020]}
        )

        resultado = gasto_per_capita(df)

        assert "ano" in resultado.columns
        assert resultado.iloc[0]["ano"] == 2020

    def test_nao_modifica_dataframe_original(self):
        df = pd.DataFrame({"Valor": [100.0], "População": [10]})

        gasto_per_capita(df)

        assert "valor_per_capita" not in df.columns