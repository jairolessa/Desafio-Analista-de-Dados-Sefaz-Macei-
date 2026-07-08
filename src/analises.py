import pandas as pd

from src.indicadores import taxa_execucao


def rankear_taxa_execucao(df: pd.DataFrame, conta: str, ano: int) -> pd.DataFrame:
    
    taxa = taxa_execucao(df[df["ano"] == ano])
    recorte = taxa[taxa["Conta"] == conta].sort_values(
        "taxa_execucao", ascending=False
    ).reset_index(drop=True)
    recorte.index += 1
    recorte.index.name = "posicao"
    return recorte.reset_index()


def matriz_posicoes(
    df: pd.DataFrame, conta: str, anos: list, top_n: int = 10
) -> pd.DataFrame:
    
    posicoes_por_ano = {}
    for ano in anos:
        ranking = rankear_taxa_execucao(df, conta=conta, ano=ano)
        posicoes_por_ano[ano] = ranking.set_index("Instituição")["posicao"]

    tabela = pd.DataFrame(posicoes_por_ano)
    capitais_relevantes = tabela.index[(tabela <= top_n).any(axis=1)]
    return tabela.loc[capitais_relevantes]


def evolucao_execucao_vs_demais(
    df: pd.DataFrame, conta: str, capital: str, anos: list
) -> pd.DataFrame:
    
    taxa = taxa_execucao(df[df["ano"].isin(anos)])
    recorte = taxa[taxa["Conta"] == conta]

    e_capital = recorte["Instituição"].str.contains(capital)

    linha_capital = recorte[e_capital][["ano", "taxa_execucao"]].rename(
        columns={"taxa_execucao": "capital"}
    )

    demais = recorte[~e_capital]
    agregado_demais = (
        demais.groupby("ano")["taxa_execucao"]
        .agg(media_demais="mean", min_demais="min", max_demais="max")
        .reset_index()
    )

    return linha_capital.merge(agregado_demais, on="ano").sort_values("ano").reset_index(drop=True)


def taxa_execucao_media_periodo(df: pd.DataFrame, anos: list) -> pd.DataFrame:
    
    taxa = taxa_execucao(df[df["ano"].isin(anos)])
    return (
        taxa.groupby(["Instituição", "Conta"])
        .agg(
            taxa_execucao_media=("taxa_execucao", "mean"),
            empenhado_medio=("empenhado", "mean"),
        )
        .reset_index()
    )


def melhor_e_pior_funcao(
    resumo: pd.DataFrame, limiar_participacao: float = 0.01
) -> pd.DataFrame:
    
    resultados = []
    for instituicao, grupo in resumo.groupby("Instituição"):
        total = grupo["empenhado_medio"].sum()
        if total <= 0:
            continue
        relevantes = grupo[grupo["empenhado_medio"] / total >= limiar_participacao]
        if relevantes.empty:
            continue

        melhor = relevantes.loc[relevantes["taxa_execucao_media"].idxmax()]
        pior = relevantes.loc[relevantes["taxa_execucao_media"].idxmin()]
        resultados.append(
            {
                "Instituição": instituicao,
                "melhor_funcao": melhor["Conta"],
                "melhor_taxa": melhor["taxa_execucao_media"],
                "pior_funcao": pior["Conta"],
                "pior_taxa": pior["taxa_execucao_media"],
            }
        )

    return pd.DataFrame(resultados)


def composicao_pareto(
    df: pd.DataFrame,
    capital: str,
    ano: int,
    nivel: str = "funcao",
    filtro_conta: str | None = None,
) -> pd.DataFrame:
    
    recorte = df[
        (df["Instituição"].str.contains(capital))
        & (df["ano"] == ano)
        & (df["tipo_conta"] == nivel)
        & (df["Coluna"] == "Despesas Empenhadas")
    ]

    if filtro_conta is not None:
        recorte = recorte[recorte["Conta"].str.startswith(filtro_conta)]

    agregado = (
        recorte.groupby("Conta")["Valor"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Valor": "valor"})
    )

    total = agregado["valor"].sum()
    agregado["percentual"] = agregado["valor"] / total * 100
    agregado["percentual_acumulado"] = agregado["percentual"].cumsum()

    return agregado
