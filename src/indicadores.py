import pandas as pd


def taxa_execucao(df: pd.DataFrame) -> pd.DataFrame:
    
    df_funcoes = df[df["tipo_conta"] == "funcao"]

    pivot = df_funcoes.pivot_table(
        index=["Instituição", "Conta", "ano"],
        columns="Coluna",
        values="Valor",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()
    pivot.columns.name = None

    pivot = pivot.rename(
        columns={"Despesas Empenhadas": "empenhado", "Despesas Pagas": "pago"}
    )
    for coluna_obrigatoria in ("empenhado", "pago"):
        if coluna_obrigatoria not in pivot.columns:
            pivot[coluna_obrigatoria] = 0.0

    pivot["taxa_execucao"] = pivot["pago"] / pivot["empenhado"]
    pivot.loc[pivot["empenhado"] == 0, "taxa_execucao"] = pd.NA

    return pivot[["Instituição", "Conta", "ano", "empenhado", "pago", "taxa_execucao"]]


def gasto_per_capita(df: pd.DataFrame) -> pd.DataFrame:
    
    resultado = df.copy()
    resultado["valor_per_capita"] = resultado["Valor"] / resultado["População"]
    return resultado