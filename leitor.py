# Tirar o texto de dentro de um PDF de forma limpa.

import pdfplumber as pl

def extrair_texto_pdf(caminho_arquivo):
    texto_completo=""
    # A biblioteca abre o arquivo e lê cada página
    with pl.open(caminho_arquivo) as pdf:
        for pagina in pdf.pages:
            # Puxa o conteúdo de forma estruturada
            texto_completo += pagina.extract_text() + "\n"
    return texto_completo