from modelos import ProdutoAnalisado
from modelos import AtributoNCM

def carregar_dados_demo():
    """Retorna um objeto ProdutoAnalisado estruturado para demonstração ou contingência."""
    return ProdutoAnalisado(
        descricao_comercial="Inversor de Frequência Trifásico Industrial 380V 15HP",
        ncm_sugerida="8504.40.90",
        atributos=[
            AtributoNCM(nome="Tensão de entrada", valor="380V"),
            AtributoNCM(nome="Potência nominal", valor="15 HP (11 kW)"),
            AtributoNCM(nome="Frequência", valor="50/60 Hz"),
            AtributoNCM(nome="Marca", valor="IndustrialTech")
        ]
    )