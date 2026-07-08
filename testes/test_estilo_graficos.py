from src.estilo_graficos import nome_curto, cores_destacando, COR_DESTAQUE, COR_BASE


class TestNomeCurto:
    def test_prefixo_de(self):
        assert nome_curto("Prefeitura Municipal de Maceió - AL") == "Maceió/AL"

    def test_prefixo_do_rio_de_janeiro(self):
        
        assert (
            nome_curto("Prefeitura Municipal do Rio de Janeiro - RJ")
            == "Rio de Janeiro/RJ"
        )

    def test_nome_composto(self):
        assert nome_curto("Prefeitura Municipal de Belo Horizonte - MG") == "Belo Horizonte/MG"


class TestCoresDestacando:
    def test_destaca_apenas_a_capital_pedida(self):
        instituicoes = [
            "Prefeitura Municipal de Maceió - AL",
            "Prefeitura Municipal de Salvador - BA",
        ]

        cores = cores_destacando(instituicoes, capital="Maceió")

        assert cores == [COR_DESTAQUE, COR_BASE]

    def test_nenhuma_capital_bate_retorna_so_cor_base(self):
        instituicoes = ["Prefeitura Municipal de Salvador - BA"]

        cores = cores_destacando(instituicoes, capital="Maceió")

        assert cores == [COR_BASE]
