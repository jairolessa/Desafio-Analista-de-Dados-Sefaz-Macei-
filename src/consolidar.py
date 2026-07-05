import re
from pathlib import Path

import duckdb
import pandas as pd


def converter_valor_br(valor_str: str) -> float:
    
    if valor_str is None:
        raise ValueError("valor_str não pode ser None")

    valor_str = valor_str.strip()
    if not valor_str:
        raise ValueError("valor_str não pode ser vazio")

    negativo = False
    if valor_str.startswith("-"):
        negativo = True
        valor_str = valor_str[1:].strip()
    elif valor_str.startswith("(") and valor_str.endswith(")"):
        
        negativo = True
        valor_str = valor_str[1:-1].strip()

    
    valor_normalizado = valor_str.replace(".", "").replace(",", ".")

    valor = float(valor_normalizado)
    return -valor if negativo else valor


def classificar_conta(conta: str) -> str:
    
    conta = conta.strip()

    if re.match(r"^\d{2}\.\d{3}\s*-", conta):
        return "subfuncao"
    if re.match(r"^\d{2}\s*-", conta):
        return "funcao"
    return "agregado"


def ler_finbra_csv(caminho_csv: Path, ano: int) -> pd.DataFrame:
    
    df = pd.read_csv(
        caminho_csv,
        sep=";",
        skiprows=3,
        encoding="latin-1",
        dtype=str,
    )

    df["Cod.IBGE"] = df["Cod.IBGE"].astype(int)
    df["População"] = df["População"].astype(int)
    df["Valor"] = df["Valor"].apply(converter_valor_br)
    df["tipo_conta"] = df["Conta"].apply(classificar_conta)
    df["ano"] = ano

    return df


def consolidar_anos(diretorio_extraido: Path) -> pd.DataFrame:
    
    if not diretorio_extraido.exists():
        return pd.DataFrame()

    dataframes = []
    for pasta_ano in sorted(diretorio_extraido.iterdir()):
        if not pasta_ano.is_dir():
            continue
        try:
            ano = int(pasta_ano.name)
        except ValueError:
            continue

        caminho_csv = pasta_ano / "finbra.csv"
        if not caminho_csv.exists():
            continue

        dataframes.append(ler_finbra_csv(caminho_csv, ano))

    if not dataframes:
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)


def salvar_parquet(df: pd.DataFrame, caminho_saida: Path) -> Path:
    
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(caminho_saida, index=False)
    return caminho_saida


def consultar_duckdb(query: str, caminho_parquet: Path) -> pd.DataFrame:
    
    conexao = duckdb.connect(database=":memory:")
    relacao = conexao.read_parquet(str(caminho_parquet))
    conexao.register("finbra", relacao)
    return conexao.execute(query).df()


if __name__ == "__main__":
    raiz_projeto = Path(__file__).resolve().parent.parent
    diretorio_extraido = raiz_projeto / "dados_extraidos"
    caminho_parquet = raiz_projeto / "dados_consolidados" / "finbra_consolidado.parquet"

    df_consolidado = consolidar_anos(diretorio_extraido)
    if df_consolidado.empty:
        print(
            f"Nenhum dado encontrado em {diretorio_extraido}. "
            "Rode codigo/extrair.py primeiro."
        )
    else:
        salvar_parquet(df_consolidado, caminho_parquet)
        print(f"Consolidado salvo em {caminho_parquet} ({len(df_consolidado)} linhas)")