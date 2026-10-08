import pdfplumber as pl
import pandas as pd
import json
import xmltodict

# Tirar o texto de dentro de um PDF de forma limpa.
def extrair_texto_pdf(caminho_arquivo):
    texto_completo=""
    # A biblioteca abre o arquivo e lê cada página
    with pl.open(caminho_arquivo) as pdf:
        for pagina in pdf.pages:
            # Puxa o conteúdo de forma estruturada
            texto_completo += pagina.extract_text() + "\n"
    return texto_completo

# Identificar o tipo de arquivo enviado e extrair o conteúdo para texto
def extrair_conteudo(uploaded_file):
    nome_arquivo = uploaded_file.name

    # PDF
    if nome_arquivo.endswith(".pdf"):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        return extrair_texto_pdf("temp.pdf")

    #Excel
    elif nome_arquivo.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
        return df.to_string(index=False)

    # CSV
    elif nome_arquivo.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df.to_string(index=False)

    # JSON
    elif nome_arquivo.endswith(".json"):
        dados = json.load(uploaded_file)
        return json.dumps(dados, indent=2)

    # XML
    elif nome_arquivo.endswith(".xml"):
        dados_dict = xmltodict.parse(uploaded_file.read())
        return json.dumps(dados_dict, indent=2)

    else:
        return "Formato não suportado"


