import zipfile
from pathlib import Path

import pandas as pd
import pytest

from main import executar_pipeline


def _criar_zip_com_csv_real(caminho_zip: Path) -> None:
   
    conteudo = (
        "Exercício: 2020\n"
        "Escopo: Capitais\n"
        "Tabela: Despesas por Função (Anexo I-E)\n"
        "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
        'Prefeitura Municipal de Maceió - AL;2704302;AL;1025360;"Despesas Empenhadas";'
        '"10 - Saúde";"siconfi-cor_TotalDespesas";100000,00\n'
    )
    caminho_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(caminho_zip, "w") as zf:
        zf.writestr("finbra.csv", conteudo.encode("latin-1"))


class TestExecutarPipeline:
    def test_pipeline_completo_gera_parquet_com_dados_corretos(self, tmp_path):
        dados_compactos = tmp_path / "dados_compactos"
        dados_extraidos = tmp_path / "dados_extraidos"
        caminho_parquet = tmp_path / "dados_consolidados" / "finbra_consolidado.parquet"

        _criar_zip_com_csv_real(dados_compactos / "2020" / "finbra.zip")

        df = executar_pipeline(dados_compactos, dados_extraidos, caminho_parquet)

        assert len(df) == 1
        assert df.iloc[0]["ano"] == 2020
        assert df.iloc[0]["Instituição"] == "Prefeitura Municipal de Maceió - AL"
        assert caminho_parquet.exists()

        df_lido = pd.read_parquet(caminho_parquet)
        pd.testing.assert_frame_equal(df, df_lido)

    def test_varios_anos_sao_todos_consolidados(self, tmp_path):
        dados_compactos = tmp_path / "dados_compactos"
        dados_extraidos = tmp_path / "dados_extraidos"
        caminho_parquet = tmp_path / "saida.parquet"

        _criar_zip_com_csv_real(dados_compactos / "2020" / "finbra.zip")
        _criar_zip_com_csv_real(dados_compactos / "2021" / "finbra.zip")

        df = executar_pipeline(dados_compactos, dados_extraidos, caminho_parquet)

        assert set(df["ano"].unique()) == {2020, 2021}

    def test_sem_zips_retorna_vazio_e_nao_gera_parquet(self, tmp_path):
        dados_compactos = tmp_path / "dados_compactos"
        dados_compactos.mkdir()
        dados_extraidos = tmp_path / "dados_extraidos"
        caminho_parquet = tmp_path / "dados_consolidados" / "finbra_consolidado.parquet"

        df = executar_pipeline(dados_compactos, dados_extraidos, caminho_parquet)

        assert df.empty
        assert not caminho_parquet.exists()