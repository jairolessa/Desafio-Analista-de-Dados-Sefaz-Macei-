import pytest

from src.consolidar import converter_valor_br, classificar_conta


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

    def test_valor_espacos_bordas(self):
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