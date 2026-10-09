# Forçar a IA a devolver os dados nas exatas colunas exigidas (Siscomex)

from pydantic import BaseModel, Field

# Define como é a linha de um atributo
class AtributoNCM(BaseModel):
    nome: str = Field(description="Nome do atributo, ex:Voltagem, Marca, Material")
    valor: str = Field(description="Valor encontrado na Invoice para este atributo")

# Uma NCM candidata, com a probabilidade estimada
class CandidataNCM(BaseModel):
    ncm: str = Field(description="Código NCM com 8 dígitos, somente números")
    descricao_ncm: str = Field(description="Descrição oficial resumida da NCM")
    probabilidade: float = Field(
        description="Probabilidade (0 a 100) de esta ser a NCM correta. A soma de todas as candidatas deve dar 100"
    )
    justificativa: str = Field(description="Em uma frase: por que esta NCM se aplica (ou por que é menos provável)")
    aliquota_ii: float = Field(description="Alíquota estimada do Imposto de Importação, em % (ex: 14.0)")
    aliquota_ipi: float = Field(description="Alíquota estimada do IPI, em % (ex: 5.0)")


# Define o produto final que engloba tudo
class ProdutoAnalisado(BaseModel):
    descricao_comercial: str = Field(description="Descrição clara do produto em português")
    candidatas: list[CandidataNCM] = Field(
        description="De 3 a 5 NCMs candidatas, da mais provável para a menos provável"
    )
    atributos: list[AtributoNCM] = Field(description="Lista dos atributos encontrados")

    @property
    def ncm_sugerida(self) -> str:
        return self.candidatas[0].ncm if self.candidatas else ""