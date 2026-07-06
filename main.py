from pathlib import Path

import pandas as pd

from src.extrair import extrair_todos
from src.consolidar import consolidar_anos, salvar_parquet


def executar_pipeline(
    dados_compactos: Path, dados_extraidos: Path, caminho_parquet: Path
) -> pd.DataFrame:
    
    destinos = extrair_todos(dados_compactos, dados_extraidos)
    if not destinos:
        return pd.DataFrame()

    df = consolidar_anos(dados_extraidos)
    if not df.empty:
        salvar_parquet(df, caminho_parquet)

    return df


def main() -> None:
    raiz_projeto = Path(__file__).resolve().parent
    dados_compactos = raiz_projeto / "dados_compactos"
    dados_extraidos = raiz_projeto / "dados_extraidos"
    caminho_parquet = raiz_projeto / "dados_consolidados" / "finbra_consolidado.parquet"

    print(f"[1/3] Extraindo zips de {dados_compactos}...")
    df = executar_pipeline(dados_compactos, dados_extraidos, caminho_parquet)

    if df.empty:
        print(f"  Nenhum .zip encontrado em {dados_compactos}. Abortando.")
        return

    print(f"[2/3] {len(df)} linhas consolidadas, {df['ano'].nunique()} ano(s).")
    print(f"[3/3] Parquet salvo em {caminho_parquet}")
    print("Pipeline concluído.")


if __name__ == "__main__":
    main()