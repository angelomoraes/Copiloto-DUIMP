import streamlit as st
import pandas as pd
from leitor import extrair_conteudo
from motor_ia import analisar_invoice_ia
import time

st.title(" DUIMP COPILOT - Catálogo de Produtos")

arquivo_enviado = st.file_uploader("Envie o documento (PDF, Excel, CSV, JSON OU XML)", type=["pdf","xlsx","xls","csv","json","xml"])

# Inicializando variáveis na memória
if "resultado_ia" not in st.session_state:
    st.session_state.resultado_ia = None
if "arquivo_atual" not in st.session_state:
    st.session_state.arquivo_atual = None
if "aprovado" not in st.session_state:
    st.session_state.aprovado = False

if arquivo_enviado is not None:
    # Se for enviado novo arquivo, limpa dados da memória
    if st.session_state.arquivo_atual != arquivo_enviado.name:
        st.session_state.arquivo_atual = arquivo_enviado.name
        st.session_state.resultado_ia = None
        st.session_state.aprovado = False

    # Mensagem enquanto processa
    if st.session_state.resultado_ia is None:
        with st.spinner("Lendo documento e acionando IA..."):
            time.sleep(1)
            texto_extraido = extrair_conteudo(arquivo_enviado)
            time.sleep(1)
            # Chama o motor de IA
            try:
                st.session_state.resultado_ia = analisar_invoice_ia(texto_extraido)
            except Exception as e:
                st.error(f"Falha na comunicação com a IA. Tente novamente em alguns instantes... Error: {e}")
                st.stop()

    resultado_ia = st.session_state.resultado_ia

    # Exibe resultados para revisão humana
    st.subheader(f"Produto Identificado: {resultado_ia.descricao_comercial}")
    st.write(f"**NCM Sugerida:** {resultado_ia.ncm_sugerida}")

    st.markdown("### Revisão de Atributos")

    # Converte lista de atributos (Pydantic) para DataFrame
    dados_tabela = [{"Atributo": attr.nome, "Valor Extraído": attr.valor} for attr in resultado_ia.atributos]
    df = pd.DataFrame(dados_tabela)

    # Cria tabela interativa
    df_editado = st.data_editor(df, num_rows="dynamic", width='stretch')

    # Botao final
    if st.button("Aprovar Lote e Exportar JSON"):
        st.session_state.aprovado = True
        
    if st.session_state.aprovado:
        json_final = df_editado.to_json(orient="records")
        st.success("Revisão concluída! Arquivo pronto para o Portal Único")
        st.download_button("Baixar Carga Siscomex", data=json_final, file_name="carga_duimp.json")

        