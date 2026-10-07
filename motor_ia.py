# Enviar o texto do PDF para IA (Gemini) e exigir que devolva no formato (Pydantic)

import os
from google import genai
from modelos import ProdutoAnalisado

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analisar_invoice_ia(texto_invoice):
    prompt = f"""
    Você é um auditor aduaneiro. Analise o texto da invoice abaixo.
    Identifique o produto principal, sugira a NCM e extraia os atributos técnicos obrigatórios.

    Texto da Invoice:
    {texto_invoice}
    """

    # A definição da estrutura ocorre ao passar o 'response_schema'
    resposta = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': ProdutoAnalisado,
        },
    )
    
    # Retorno como objeto Python, pronto para virar tabela
    return resposta.parsed
