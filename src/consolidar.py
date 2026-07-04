import re


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
        # formato contábil alternativo, por segurança
        negativo = True
        valor_str = valor_str[1:-1].strip()

    # remove separador de milhar e troca vírgula decimal por ponto
    valor_normalizado = valor_str.replace(".", "").replace(",", ".")

    valor = float(valor_normalizado)  # deixa o ValueError nativo propagar
    return -valor if negativo else valor


def classificar_conta(conta: str) -> str:
    
    conta = conta.strip()

    if re.match(r"^\d{2}\.\d{3}\s*-", conta):
        return "subfuncao"
    if re.match(r"^\d{2}\s*-", conta):
        return "funcao"
    return "agregado"