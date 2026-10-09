from modelos import ProdutoAnalisado, CandidataNCM, AtributoNCM


def carregar_dados_demo():
    """Retorna um objeto ProdutoAnalisado estruturado para demonstração ou contingência.
    NCMs, probabilidades e alíquotas são ilustrativas."""
    return ProdutoAnalisado(
        descricao_comercial="Inversor de Frequência Trifásico Industrial 380V 15HP",
        candidatas=[
            CandidataNCM(
                ncm="85044090",
                descricao_ncm="Conversores estáticos - outros",
                probabilidade=70,
                justificativa="Inversor de frequência é um conversor estático de energia elétrica.",
                aliquota_ii=14.0,
                aliquota_ipi=5.0,
            ),
            CandidataNCM(
                ncm="85371090",
                descricao_ncm="Quadros/painéis de comando para tensão não superior a 1.000 V - outros",
                probabilidade=20,
                justificativa="Possível se o equipamento for importado como painel de comando completo.",
                aliquota_ii=14.0,
                aliquota_ipi=5.0,
            ),
            CandidataNCM(
                ncm="85049090",
                descricao_ncm="Partes de transformadores e conversores estáticos - outras",
                probabilidade=10,
                justificativa="Menos provável: só se for importado como parte/módulo, não como equipamento completo.",
                aliquota_ii=14.0,
                aliquota_ipi=5.0,
            ),
        ],
        atributos=[
            AtributoNCM(nome="Tensão de entrada", valor="380V"),
            AtributoNCM(nome="Potência nominal", valor="15 HP (11 kW)"),
            AtributoNCM(nome="Frequência", valor="50/60 Hz"),
            AtributoNCM(nome="Marca", valor="IndustrialTech"),
        ],
    )