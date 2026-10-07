# Forçar a IA a devolver os dados nas exatas colunas exigidas (Siscomex)

from pydantic import BaseModel, Field

# Define como é a linha de um atributo
class AtributoNCM(BaseModel):
    nome : str = Field(description="Nome do atributo, ex:Voltagem, Marca, Material")
    valor : str = Field(description="Valor encontrado na Invoice para este atributo")

# Define o produto final que engloba tudo
class ProdutoAnalisado(BaseModel):
    descricao_comercial : str = Field(description="Descrição clara do atributo em português")
    ncm_sugerida : str = Field(description="Código NCM com 8 dígitos")
    atributos : list[AtributoNCM] = Field(description="Lista dos atributos encontrados")