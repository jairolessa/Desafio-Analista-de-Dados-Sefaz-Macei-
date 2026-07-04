import zipfile
from pathlib import Path

import pytest

from src.extrair import encontrar_zips, extrair_zip, extrair_todos


def _criar_zip(caminho_zip: Path, nome_interno: str, conteudo: str) -> None:
    
    caminho_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(caminho_zip, "w") as zf:
        zf.writestr(nome_interno, conteudo)


class TestEncontrarZips:
    def test_localiza_um_zip_por_ano(self, tmp_path):
        base = tmp_path / "dados_compactos"
        _criar_zip(base / "2020" / "finbra_CAP (1).zip", "finbra.csv", "conteudo 2020")
        _criar_zip(base / "2021" / "finbra_CAP.zip", "finbra.csv", "conteudo 2021")

        encontrados = encontrar_zips(base)

        anos = [ano for ano, _ in encontrados]
        assert anos == [2020, 2021]

    def test_ignora_pastas_que_nao_sao_ano(self, tmp_path):
        base = tmp_path / "dados_compactos"
        _criar_zip(base / "2020" / "finbra.zip", "finbra.csv", "conteudo")
        (base / ".git").mkdir(parents=True)

        encontrados = encontrar_zips(base)

        assert len(encontrados) == 1
        assert encontrados[0][0] == 2020

    def test_diretorio_vazio_retorna_lista_vazia(self, tmp_path):
        base = tmp_path / "dados_compactos"
        base.mkdir()

        assert encontrar_zips(base) == []

    def test_ignora_arquivos_que_nao_sao_zip_dentro_do_ano(self, tmp_path):
        base = tmp_path / "dados_compactos"
        pasta_2020 = base / "2020"
        pasta_2020.mkdir(parents=True)
        (pasta_2020 / "leiame.txt").write_text("nao é zip")
        _criar_zip(pasta_2020 / "finbra.zip", "finbra.csv", "conteudo")

        encontrados = encontrar_zips(base)

        assert len(encontrados) == 1
        assert encontrados[0][1].suffix == ".zip"


class TestExtrairZip:
    def test_extrai_conteudo_do_zip(self, tmp_path):
        zip_path = tmp_path / "finbra.zip"
        _criar_zip(zip_path, "finbra.csv", "Exercício: 2020\nlinha,de,dado")
        destino = tmp_path / "saida"

        extrair_zip(zip_path, destino)

        arquivo_extraido = destino / "finbra.csv"
        assert arquivo_extraido.exists()
        assert "Exercício: 2020" in arquivo_extraido.read_text(encoding="utf-8")

    def test_cria_diretorio_destino_se_nao_existir(self, tmp_path):
        zip_path = tmp_path / "finbra.zip"
        _criar_zip(zip_path, "finbra.csv", "conteudo")
        destino = tmp_path / "pasta" / "que" / "nao" / "existe"

        extrair_zip(zip_path, destino)

        assert (destino / "finbra.csv").exists()

    def test_e_idempotente_pode_rodar_duas_vezes(self, tmp_path):
        zip_path = tmp_path / "finbra.zip"
        _criar_zip(zip_path, "finbra.csv", "conteudo")
        destino = tmp_path / "saida"

        extrair_zip(zip_path, destino)
        extrair_zip(zip_path, destino)  # não pode levantar erro

        assert (destino / "finbra.csv").exists()


class TestExtrairTodos:
    def test_organiza_extracao_por_ano(self, tmp_path):
        base = tmp_path / "dados_compactos"
        saida = tmp_path / "dados_extraidos"
        _criar_zip(base / "2020" / "finbra.zip", "finbra.csv", "dado 2020")
        _criar_zip(base / "2021" / "finbra.zip", "finbra.csv", "dado 2021")

        destinos = extrair_todos(base, saida)

        assert (saida / "2020" / "finbra.csv").read_text() == "dado 2020"
        assert (saida / "2021" / "finbra.csv").read_text() == "dado 2021"
        assert len(destinos) == 2

    def test_base_vazia_nao_extrai_nada(self, tmp_path):
        base = tmp_path / "dados_compactos"
        base.mkdir()
        saida = tmp_path / "dados_extraidos"

        assert extrair_todos(base, saida) == []