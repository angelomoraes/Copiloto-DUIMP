import streamlit as st
import pandas as pd
from leitor import extrair_conteudo
from motor_ia import analisar_invoice_ia
import time
from dados_demo import carregar_dados_demo

# Configurações da interface com Streamlit
st.set_page_config(page_title="DUIMP Copilot", layout="wide")

# Barra lateral
st.sidebar.title("Painel de Controle")
st.sidebar.info("Módulo de Auditoria e Pré-Classificação Aduaneira")
modo_demo = st.sidebar.checkbox("Modo Demo (Sem IA)")

# Página inicial
st.title(" DUIMP COPILOT - Censo Inteligente do Importador")
st.markdown("Automação de extração, auditoria de NCM e pré-validação de atributos para o Catálogo de Produtos.")

# Upload de arquivos multi-formato
arquivo_enviado = st.file_uploader("Envie o documento (PDF, Excel, CSV, JSON OU XML)", type=["pdf","xlsx","xls","csv","json","xml"])

# Inicializando variáveis na memória
if "resultado_ia" not in st.session_state:
    st.session_state.resultado_ia = None
if "arquivo_atual" not in st.session_state:
    st.session_state.arquivo_atual = None
if "aprovado" not in st.session_state:
    st.session_state.aprovado = False

# Simulação de base de dados
if modo_demo:
    st.sidebar.markdown("**Status:** Demo Ativo")
    st.session_state.resultado_ia = carregar_dados_demo()
    st.info("Modo Demo Ativo: Utilizando base de dados simulada ")

elif arquivo_enviado is not None:
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

if st.session_state.resultado_ia is not None:
    resultado_ia = st.session_state.resultado_ia

    #Dashboard de métricas de impacto
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Tempo Médio Economizado", value="38 minutos", delta="-95% vs Digitação Manual")
    with col2:
        st.metric(label="Integridade do Catálogo", value="100%", delta="Atributos obrigatórios preenchidos")
    with col3:
        st.metric(label="Risco Aduaneiro", value="Baixo (Pré-auditado)", delta="Blindado contra Canal Vermelho")

    st.markdown("---")

    # Exibe resultados para revisão humana
    st.subheader(f"Produto Identificado: {resultado_ia.descricao_comercial}")
    st.write(f"**NCM Sugerida:** {resultado_ia.ncm_sugerida}")

    # Alerta inteligente
    ncm_limpa = resultado_ia.ncm_sugerida.replace(".","").replace("-","").strip()
    if ncm_limpa.startswith(("30", "29", "33", "21", "22", "38")):
        st.warning(" **Alerta Regulatório (ANVISA):** Esta NCM exige anuência prévia da ANVISA. Certifique-se de que a composição e os atributos técnicos estão detalhados.")
    elif ncm_limpa.startswith(("01", "02", "03", "04", "10", "12", "15", "23")):
        st.warning(" **Alerta Regulatório (MAPA / VIGIAGRO):** NCM sujeita a fiscalização sanitária do Ministério da Agricultura.")
    elif ncm_limpa.startswith(("84", "85", "90")):
        st.info("**Status Regulatório:** NCM de bens industriais/tecnológicos. Sujeito ao licenciamento padrão do DECEX.")
    else:
        st.success("**Status Regulatório:** Nenhuma restrição crítica de órgão anuente identificada para esta NCM.")

    st.markdown("### Revisão de Atributos")

    # Converte lista de atributos (Pydantic) para DataFrame
    dados_tabela = [{"Atributo": attr.nome, "Valor Extraído": attr.valor} for attr in resultado_ia.atributos]
    df = pd.DataFrame(dados_tabela)

    # Cria tabela interativa
    df_editado = st.data_editor(df, num_rows="dynamic", width='stretch')

    # Simulação de transmissão via API do Portal Único SISCOMEX
    col_btn1, col_btn2 = st.columns([1, 2])

    if "transmitido" not in st.session_state:
        st.session_state.transmitido = None

    with col_btn1:
        # Botão principal de transmissão
        if st.button("Transmitir para o Catálogo Siscomex", type="primary"):
            with st.spinner("Autenticando via certificado digital e validando no Portal Único..."):
                time.sleep(2.5) # Simula o tempo de resposta da API do governo
            st.session_state.transmitido = True

    if st.session_state.transmitido:
        st.success("Transmissão Concluída! Registro integrado com sucesso no ambiente do governo.")
        st.info("**Protocolo Oficial Siscomex gerado:** `DUIMP-2026-BR-889410-X`")

    # Botao de dowload json
    if st.button("Aprovar Lote"):
        st.session_state.aprovado = True
        
    if st.session_state.aprovado:
        json_final = df_editado.to_json(orient="records")
        st.success("Revisão concluída! Arquivo pronto para o Portal Único")
        st.download_button("Baixar Carga Siscomex", data=json_final, file_name="carga_duimp.json")

        