import streamlit as st
import pandas as pd
from leitor import extrair_texto_pdf
from motor_ia import analisar_invoice_ia
import time

st.title(" DUIMP COPILOT - Catálogo de Produtos")

arquivo_pdf = st.file_uploader("Suba a Invoice (PDF)", type=["pdf"])

if arquivo_pdf is not None:
    # Mensagem enquanto processa
    with st.spinner("Lendo documento e acionando IA..."):
        # Salva o arquivo temporariamente para o pdfplumber conseguir ler
        with open("temp.pdf", "wb") as f:
            f.write(arquivo_pdf.getbuffer())

        texto_extraido = extrair_texto_pdf("temp.pdf")

        time.sleep(1)
        #st.text(texto_extraido)

        # Chama o motor de IA
        try:
            resultado_ia = analisar_invoice_ia(texto_extraido)
        except Exception as e:
            st.error(f"Falha na comunicação com a IA. Tente novamente em alguns minutos... Error: {e}")
            st.stop()
    
        # Exibe resultados para revisão humana
        st.subheader(f"Produto Identificado: {resultado_ia.descricao_comercial}")
        st.write(f"**NCM Sugerida:** {resultado_ia.ncm_sugerida}")

        st.markdown("### Revisão de Atributos")

        # Converte lista de atributos (Pydantic) para DataFrame
        dados_tabela = [{"Atributo": attr.nome, "Valor Extraído": attr.valor} for attr in resultado_ia.atributos]
        df = pd.DataFrame(dados_tabela)

        # Cria tabela interativa
        df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # Botao final
    if st.button("Aprovar Lote e Exportar JSON"):
        json_final = df_editado.to_json(orient="records")
        st.success("Revisão concluída! Arquivo pronto para o Portal Único")
        st.download_button("Baixar Carga Siscomex", data=json_final, file_name="carga_duimp.json")

        