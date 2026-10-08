import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from openai import OpenAI
from modelos import ProdutoAnalisado

load_dotenv()


def _chaves(nome_var):
    valor = ""
    # Primeiro tenta a busca da WEB
    try:
        if nome_var in st.secrets:
            valor = st.secrets[nome_var]
    except Exception:
        pass
    
    # Se não achou, busca do ambiente local (.env)
    if not valor:
        valor = os.getenv(nome_var, "")

    return [k.strip() for k in valor.split(",") if k.strip()]

def _get_env(nome_var, default=""):
    # Tenta buscar variáveis de configuraçãode forma segura
    try:
        if nome_var in st.secrets:
            return st.secrets[nome_var]
    except Exception:
        pass
    return os.getenv(nome_var, default)

# A ordem da lista é a ordem de prioridade
PROVEDORES = [
    {"nome": "Gemini", "tipo": "gemini",
     "chaves": _chaves("GEMINI_API_KEYS"), "modelo": _get_env("GEMINI_MODEL")},
    {"nome": "Groq", "tipo": "openai", "base_url": "https://api.groq.com/openai/v1",
     "chaves": _chaves("GROQ_API_KEYS"), "modelo": _get_env("GROQ_MODEL")},
    {"nome": "OpenRouter", "tipo": "openai", "base_url": "https://openrouter.ai/api/v1",
     "chaves": _chaves("OPENROUTER_API_KEYS"), "modelo": _get_env("OPENROUTER_MODEL")},
]


def _montar_prompt(texto_invoice):
    return f"""
    Você é um auditor aduaneiro. Analise o texto da invoice abaixo.
    Identifique o produto principal, sugira a NCM e extraia os atributos técnicos obrigatórios.

    Texto da Invoice:
    {texto_invoice}
    """


def _chamar_gemini(chave, modelo, prompt):
    client = genai.Client(api_key=chave)
    resp = client.models.generate_content(
        model=modelo,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ProdutoAnalisado,
        },
    )
    if resp.parsed is None:
        raise ValueError("Gemini devolveu um JSON fora do formato esperado")
    return resp.parsed


def _chamar_openai_compat(base_url, chave, modelo, prompt):
    # Esses provedores não aceitam o schema direto, então pedimos JSON no prompt
    # e validamos com o Pydantic no final.
    schema = ProdutoAnalisado.model_json_schema()
    prompt_json = (
        prompt
        + f"\n\nResponda APENAS com um JSON válido que siga este schema:\n{schema}"
    )
    client = OpenAI(api_key=chave, base_url=base_url)
    resp = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt_json}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    conteudo = resp.choices[0].message.content.strip()
    conteudo = conteudo.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return ProdutoAnalisado.model_validate_json(conteudo)


def analisar_invoice_ia(texto_invoice):
    prompt = _montar_prompt(texto_invoice)
    erros = []

    for prov in PROVEDORES:
        if not prov["chaves"] or not prov["modelo"]:
            continue  # provedor não configurado

        for i, chave in enumerate(prov["chaves"], start=1):
            for tentativa in range(2):  # 1 retry para erros passageiros (503)
                try:
                    if prov["tipo"] == "gemini":
                        resultado = _chamar_gemini(chave, prov["modelo"], prompt)
                    else:
                        resultado = _chamar_openai_compat(
                            prov["base_url"], chave, prov["modelo"], prompt
                        )
                    print(f"OK: {prov['nome']} (chave {i})")
                    return resultado
                except Exception as e:
                    msg = str(e)
                    erros.append(f"{prov['nome']} chave {i}: {msg[:150]}")
                    print(f"Falhou: {erros[-1]}")
                    # Cota estourada (429) ou chave inválida: não adianta repetir
                    if "429" in msg or "401" in msg or "403" in msg or "404" in msg:
                        break
                    time.sleep(2)  # espera 3s, 6s, 9s, 12s

    raise RuntimeError("Todos os provedores falharam:\n" + "\n".join(erros))