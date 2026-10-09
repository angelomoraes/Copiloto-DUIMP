# Estimativa de perda financeira ao classificar uma NCM errada.
# ATENÇÃO: valores de referência. Confirme multas e alíquotas com seu despachante/contador.

MULTA_CLASSIFICACAO = 0.01   # 1% do valor aduaneiro por classificação incorreta
MULTA_DIFERENCA = 0.75       # 75% sobre a diferença de tributos recolhida a menos


def tributos(valor_aduaneiro, aliquota_ii, aliquota_ipi):
    """II + IPI (o IPI incide sobre valor + II)."""
    ii = valor_aduaneiro * aliquota_ii / 100
    ipi = (valor_aduaneiro + ii) * aliquota_ipi / 100
    return ii + ipi


def perda_se_errar(valor_aduaneiro, escolhida, real):
    """Perda se você classificou como `escolhida`, mas a NCM correta era `real`."""
    if escolhida["ncm"] == real["ncm"]:
        return {"diferenca_tributos": 0.0, "multa_classificacao": 0.0, "multa_diferenca": 0.0, "total": 0.0}

    pago = tributos(valor_aduaneiro, escolhida["aliquota_ii"], escolhida["aliquota_ipi"])
    devido = tributos(valor_aduaneiro, real["aliquota_ii"], real["aliquota_ipi"])
    diferenca = max(0.0, devido - pago)  # só há cobrança se pagou a menos

    multa_class = valor_aduaneiro * MULTA_CLASSIFICACAO
    multa_dif = diferenca * MULTA_DIFERENCA
    return {
        "diferenca_tributos": diferenca,
        "multa_classificacao": multa_class,
        "multa_diferenca": multa_dif,
        "total": diferenca + multa_class + multa_dif,
    }


def calcular_risco(valor_aduaneiro, escolhida, candidatas):
    """Retorna (perda esperada, pior caso, detalhamento por cenário)."""
    cenarios = []
    for real in candidatas:
        if real["ncm"] == escolhida["ncm"]:
            continue
        perda = perda_se_errar(valor_aduaneiro, escolhida, real)
        perda["ncm_real"] = real["ncm"]
        perda["probabilidade"] = real["probabilidade"]
        cenarios.append(perda)

    esperada = sum(c["probabilidade"] / 100 * c["total"] for c in cenarios)
    pior = max((c["total"] for c in cenarios), default=0.0)
    return esperada, pior, cenarios