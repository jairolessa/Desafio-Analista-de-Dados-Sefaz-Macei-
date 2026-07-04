import zipfile
from pathlib import Path


def encontrar_zips(diretorio_base: Path) -> list[tuple[int, Path]]:
    
    if not diretorio_base.exists():
        return []

    encontrados = []
    for pasta_ano in sorted(diretorio_base.iterdir()):
        if not pasta_ano.is_dir():
            continue
        try:
            ano = int(pasta_ano.name)
        except ValueError:
            continue

        for zip_path in sorted(pasta_ano.glob("*.zip")):
            encontrados.append((ano, zip_path))

    return encontrados


def extrair_zip(caminho_zip: Path, diretorio_destino: Path) -> Path:
    
    diretorio_destino.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(caminho_zip) as zf:
        zf.extractall(diretorio_destino)
    return diretorio_destino


def extrair_todos(diretorio_base: Path, diretorio_saida: Path) -> list[Path]:
    
    destinos = []
    for ano, zip_path in encontrar_zips(diretorio_base):
        destino_ano = diretorio_saida / str(ano)
        extrair_zip(zip_path, destino_ano)
        destinos.append(destino_ano)
    return destinos


if __name__ == "__main__":
    raiz_projeto = Path(__file__).resolve().parent.parent
    base = raiz_projeto / "dados_compactos"
    saida = raiz_projeto / "dados_extraidos"

    destinos = extrair_todos(base, saida)
    if not destinos:
        print(f"Nenhum .zip encontrado em {base}")
    for destino in destinos:
        print(f"Extraído: {destino}")