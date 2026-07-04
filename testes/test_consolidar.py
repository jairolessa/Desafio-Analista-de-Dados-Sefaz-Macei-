from pathlib import Path

import pandas as pd
import pytest

from src.consolidar import (
    converter_valor_br,
    classificar_conta,
    ler_finbra_csv,
    consolidar_anos,
)

CAMINHO_AMOSTRA = Path(__file__).parent / "amostras" / "finbra_amostra.csv"


class TestConverterValorBR:

    def test_valor_simples(self):
        assert converter_valor_br("874885274,98") == pytest.approx(874885274.98)

    def test_valor_com_milhar(self):
        assert converter_valor_br("1.234.567,89") == pytest.approx(1234567.89)

    def test_valor_com_milhar_grande(self):
        assert converter_valor_br("1.874.885.274,98") == pytest.approx(1874885274.98)

    def test_valor_negativo_anulacao_de_empenho(self):
        assert converter_valor_br("-874885274,98") == pytest.approx(-874885274.98)

    def test_valor_negativo_com_milhar(self):
        assert converter_valor_br("-1.234.567,89") == pytest.approx(-1234567.89)

    def test_valor_zero(self):
        assert converter_valor_br("0,00") == 0.0

    def test_valor_sem_casas_decimais(self):
        assert converter_valor_br("1000") == pytest.approx(1000.0)

    def test_valor_com_espacos_nas_bordas(self):
        assert converter_valor_br("  1.234,56  ") == pytest.approx(1234.56)

    def test_valor_none_levanta_erro(self):
        with pytest.raises(ValueError):
            converter_valor_br(None)

    def test_valor_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            converter_valor_br("")


class TestClassificarConta:

    def test_funcao_dois_digitos(self):
        assert classificar_conta("10 - Saúde") == "funcao"

    def test_funcao_com_zero_a_esquerda(self):
        assert classificar_conta("04 - Administração") == "funcao"

    def test_subfuncao(self):
        assert classificar_conta("10.301 - Atenção Básica") == "subfuncao"

    def test_subfuncao_outra_funcao(self):
        assert classificar_conta("12.365 - Educação Infantil") == "subfuncao"

    def test_subfuncao_administracao_geral_matricial(self):
        assert classificar_conta("10.122 - Administração Geral") == "subfuncao"

    def test_agregado_despesas_exceto_intraorcamentarias(self):
        assert classificar_conta("Despesas Exceto Intraorçamentárias") == "agregado"

    def test_agregado_despesas_intraorcamentarias(self):
        assert classificar_conta("Despesas Intraorçamentárias") == "agregado"

    def test_agregado_demais_subfuncoes(self):
        assert classificar_conta("FU10 - Demais Subfunções") == "agregado"

    def test_agregado_demais_subfuncoes_outra_funcao(self):
        assert classificar_conta("FU12 - Demais Subfunções") == "agregado"


class TestLerFinbraCsv:

    def test_pula_as_3_linhas_de_metadado(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)
        assert not df["Instituição"].str.contains("Exercício").any()

    def test_preserva_acentos_do_encoding_latin1(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        assert (df["Conta"] == "01.031 - Ação Legislativa").any()
        assert df["Instituição"].str.contains("Rio Branco").any()

    def test_remove_aspas_duplas_dos_campos(self):
       
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        assert not df["Coluna"].str.contains('"').any()
        assert not df["Conta"].str.contains('"').any()
        assert (df["Coluna"] == "Despesas Empenhadas").any()

    def test_adiciona_coluna_ano(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        assert (df["ano"] == 2020).all()

    def test_adiciona_coluna_tipo_conta(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        linha_funcao = df[df["Conta"] == "01 - Legislativa"].iloc[0]
        linha_subfuncao = df[df["Conta"] == "01.031 - Ação Legislativa"].iloc[0]
        linha_agregado = df[df["Conta"] == "Despesas Exceto Intraorçamentárias"].iloc[0]
        linha_fu = df[df["Conta"] == "FU01 - Demais Subfunções"].iloc[0]

        assert linha_funcao["tipo_conta"] == "funcao"
        assert linha_subfuncao["tipo_conta"] == "subfuncao"
        assert linha_agregado["tipo_conta"] == "agregado"
        assert linha_fu["tipo_conta"] == "agregado"

    def test_valor_convertido_para_float(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        assert pd.api.types.is_float_dtype(df["Valor"])

        linha = df[
            (df["Conta"] == "01 - Legislativa") & (df["Coluna"] == "Despesas Empenhadas")
        ].iloc[0]
        assert linha["Valor"] == pytest.approx(29014059.54)

    def test_valor_negativo_anulacao_preservado(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        negativos = df[df["Valor"] < 0]
        assert len(negativos) == 1
        assert negativos.iloc[0]["Instituição"].startswith(
            "Prefeitura Municipal de Salvador"
        )
        assert negativos.iloc[0]["Valor"] == pytest.approx(-607166.09)

    def test_diferencia_capitais_diferentes(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        assert set(df["UF"].unique()) == {"AC", "RO", "BA"}

    def test_populacao_e_ibge_como_inteiro(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)

        assert pd.api.types.is_integer_dtype(df["Cod.IBGE"])
        assert pd.api.types.is_integer_dtype(df["População"])

    def test_quantidade_de_linhas_bate_com_amostra(self):
        df = ler_finbra_csv(CAMINHO_AMOSTRA, ano=2020)
        assert len(df) == 6


class TestConsolidarAnos:
    def test_consolida_varios_anos_em_um_unico_dataframe(self, tmp_path):
        diretorio_extraido = tmp_path / "dados_extraidos"
        (diretorio_extraido / "2020").mkdir(parents=True)
        (diretorio_extraido / "2021").mkdir(parents=True)

        conteudo_amostra = CAMINHO_AMOSTRA.read_text(encoding="latin-1")
        (diretorio_extraido / "2020" / "finbra.csv").write_text(
            conteudo_amostra, encoding="latin-1"
        )
        (diretorio_extraido / "2021" / "finbra.csv").write_text(
            conteudo_amostra, encoding="latin-1"
        )

        df = consolidar_anos(diretorio_extraido)

        assert set(df["ano"].unique()) == {2020, 2021}
        assert len(df) == 12

    def test_diretorio_vazio_retorna_dataframe_vazio(self, tmp_path):
        diretorio_extraido = tmp_path / "dados_extraidos"
        diretorio_extraido.mkdir()

        df = consolidar_anos(diretorio_extraido)

        assert df.empty