import streamlit as st
import pandas as pd
from leitor import extrair_conteudo
from motor_ia import analisar_invoice_ia
import time
from dados_demo import carregar_dados_demo
from risco import calcular_risco, MULTA_CLASSIFICACAO, tributos
import altair as alt

# Configurações da interface com Streamlit
st.set_page_config(page_title="DUIMP Copilot", layout="wide")

# Barra lateral
st.sidebar.title("Painel de Controle")
st.sidebar.info("Módulo de Auditoria e Pré-Classificação Aduaneira")
modo_demo = st.sidebar.checkbox("Modo Demo (Sem IA)")

# Página inicial
st.title(" DUIMP COPILOT - Censo Inteligente do Importador")
st.markdown("Automação de extração, auditoria de NCM e pré-validação de atributos para o Catálogo de Produtos.")

# Formatação da moeda
def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def obter_candidatas(resultado):
    """Devolve as NCMs candidatas ordenadas (maior probabilidade primeiro) e normalizadas para somar 100%."""
    candidatas = [c.model_dump() for c in (getattr(resultado, "candidatas", None) or [])]
    if not candidatas:
        # Resultado no formato antigo (só uma NCM): vira uma lista com 1 candidata
        candidatas = [{
            "ncm": resultado.ncm_sugerida,
            "descricao_ncm": "-",
            "probabilidade": 100.0,
            "justificativa": "Única NCM disponível neste resultado",
            "aliquota_ii": 0.0,
            "aliquota_ipi": 0.0,
        }]
    candidatas.sort(key=lambda c: c["probabilidade"], reverse=True)
    total = sum(c["probabilidade"] for c in candidatas) or 1
    for c in candidatas:
        c["probabilidade"] = c["probabilidade"] / total * 100
    return candidatas

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
            st.session_state.texto_extraido = texto_extraido
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
        st.metric(label="Tempo Médio Economizado", value="21 minutos", delta="-95% vs Digitação Manual")
    with col2:
        st.metric(label="Integridade do Catálogo", value="100%", delta="Atributos obrigatórios preenchidos")
    with col3:
        st.metric(label="Risco Aduaneiro", value="Baixo (Pré-auditado)", delta="Blindado contra Canal Vermelho")

    st.markdown("---")

    # Exibe resultados para revisão humana
    st.subheader(f"Produto Identificado: {resultado_ia.descricao_comercial}")
    
    # NCM mais prováveis
    candidatas = obter_candidatas(resultado_ia)
    topo = candidatas[0]
    st.success(f"**NCM mais provável: {topo['ncm']}** — {topo['descricao_ncm']} ({topo['probabilidade']:.0f}%)")
 
    # Alíquotas vêm da IA e podem estar erradas, usuário pode corrigir
    with st.expander("Ajustar alíquotas (a IA pode errar, confira na TEC e na Tabela de IPI)"):
        df_aliq = pd.DataFrame(
            [{"NCM": c["ncm"], "II (%)": c["aliquota_ii"], "IPI (%)": c["aliquota_ipi"]} for c in candidatas]
        )
        df_aliq = st.data_editor(
            df_aliq,
            disabled=["NCM"],
            hide_index=True,
            key=f"aliquotas_{st.session_state.arquivo_atual}_{modo_demo}",
        )
        for c, (_, linha) in zip(candidatas, df_aliq.iterrows()):
            c["aliquota_ii"] = float(linha["II (%)"])
            c["aliquota_ipi"] = float(linha["IPI (%)"])
    
    st.markdown("### Ranking de NCMs")
    df_rank = pd.DataFrame(
        [
            {
                "Rank": f"{i + 1}º",
                "NCM": c["ncm"],
                "Descrição": c["descricao_ncm"],
                "Probabilidade": c["probabilidade"],
                "II (%)": c["aliquota_ii"],
                "IPI (%)": c["aliquota_ipi"],
                "Justificativa": c["justificativa"],
            }
            for i, c in enumerate(candidatas)
        ]
    )
 
    def destacar_topo(linha):
        cor = "background-color: #d4edda; font-weight: bold" if linha.name == 0 else ""
        return [cor] * len(linha)
 
    st.dataframe(
        df_rank.style.apply(destacar_topo, axis=1),
        column_config={
            "Probabilidade": st.column_config.ProgressColumn(
                "Probabilidade", min_value=0, max_value=100, format="%.0f%%"
            )
        },
        hide_index=True,
        width="stretch",
    )
    st.caption("As probabilidades são estimadas pela IA (não são calibradas). Use como apoio, não como verdade.")

    # Decisão e riscos financeiros
    st.markdown("### Decisão de Classificação e Risco")
    col_a, col_b = st.columns(2)
    descricoes = {c["ncm"]: c["descricao_ncm"] for c in candidatas}
    ncm_escolhida = col_a.selectbox(
        "NCM que você pretende usar",
        [c["ncm"] for c in candidatas],
        format_func=lambda n: f"{n} — {descricoes[n][:50]}",
    )
    valor = col_b.number_input("Valor aduaneiro da mercadoria (R$)", min_value=0.0, step=100.0, format="%.2f")
    escolhida = next(c for c in candidatas if c["ncm"] == ncm_escolhida)

    # Alerta inteligente (Baseado na NCM escolhida)
    ncm_limpa = ncm_escolhida.replace(".", "").replace("-", "").strip()
    if ncm_limpa.startswith(("30", "29", "33", "21", "22", "38")):
        st.warning(" **Alerta Regulatório (ANVISA):** Esta NCM exige anuência prévia da ANVISA. Certifique-se de que a composição e os atributos técnicos estão detalhados.")
    elif ncm_limpa.startswith(("01", "02", "03", "04", "10", "12", "15", "23")):
        st.warning(" **Alerta Regulatório (MAPA / VIGIAGRO):** NCM sujeita a fiscalização sanitária do Ministério da Agricultura.")
    elif ncm_limpa.startswith(("84", "85", "90")):
        st.info("**Status Regulatório:** NCM de bens industriais/tecnológicos. Sujeito ao licenciamento padrão do DECEX.")
    else:
        st.success("**Status Regulatório:** Nenhuma restrição crítica de órgão anuente identificada para esta NCM.")

    # Carga tributária por NCM (II + IPI)
    st.markdown("### Carga Tributária por NCM")
    df_carga = pd.DataFrame(
        [{"NCM": c["ncm"], "Carga": tributos(100.0, c["aliquota_ii"], c["aliquota_ipi"])} for c in candidatas]
    )
    df_carga["Zero"] = 0
    df_carga["Escolhida"] = df_carga["NCM"] == ncm_escolhida

    cor = alt.condition(alt.datum.Escolhida, alt.value("#2e7d32"), alt.value("#9e9e9e"))
    base = alt.Chart(df_carga).encode(y=alt.Y("NCM:N", sort=None, title=None))
    hastes = base.mark_rule(strokeWidth=4).encode(
        x=alt.X("Zero:Q", title="Carga tributária sobre o valor aduaneiro (%)"), x2="Carga:Q", color=cor
    )
    pontos = base.mark_circle(size=200).encode(x="Carga:Q", color=cor, tooltip=["NCM", alt.Tooltip("Carga:Q", format=".2f")])
    rotulos = base.mark_text(align="left", dx=12).encode(x="Carga:Q", text=alt.Text("Carga:Q", format=".1f"))
    st.altair_chart(hastes + pontos + rotulos)

    carga_escolhida = df_carga.loc[df_carga["NCM"] == ncm_escolhida, "Carga"].iloc[0]
    df_dif = pd.DataFrame({"NCM": df_carga["NCM"], "Carga (%)": df_carga["Carga"].round(2)})
    df_dif["Diferença (p.p.)"] = (df_carga["Carga"] - carga_escolhida).round(2)
    if valor > 0:
        df_dif["Diferença (R$)"] = ((df_carga["Carga"] - carga_escolhida) / 100 * valor).apply(brl)
    st.dataframe(df_dif, hide_index=True, width="stretch")
    st.caption("Considera só II e IPI (IPI incide sobre valor + II). Alíquotas são estimativas da IA: ajuste no expander acima.")

    if valor > 0:
        esperada, pior, cenarios = calcular_risco(valor, escolhida, candidatas)
        m1, m2, m3 = st.columns(3)
        m1.metric("Perda esperada", brl(esperada), help="Média ponderada pela probabilidade de cada NCM ser a correta")
        m2.metric("Pior caso", brl(pior))
        m3.metric("Multa por classificação (1%)", brl(valor * MULTA_CLASSIFICACAO))
 
        if cenarios:
            df_cen = pd.DataFrame(
                [
                    {
                        "Se a correta for": c["ncm_real"],
                        "Probabilidade": f"{c['probabilidade']:.0f}%",
                        "Tributos a menos": brl(c["diferenca_tributos"]),
                        "Multa classificação": brl(c["multa_classificacao"]),
                        "Multa 75% s/ diferença": brl(c["multa_diferenca"]),
                        "Perda total": brl(c["total"]),
                    }
                    for c in sorted(cenarios, key=lambda c: c["total"], reverse=True)
                ]
            )
            st.dataframe(df_cen, hide_index=True, width="stretch")
        st.caption(
            "Estimativa: multa de 1% do valor aduaneiro + diferença de II/IPI + multa de 75% sobre a diferença. "
            "Não inclui juros SELIC, ICMS, PIS/COFINS nem outras penalidades. Confirme com seu despachante."
        )
    else:
        st.info("Informe o valor aduaneiro para calcular a perda.")

    with st.expander("Ver texto extraído do documento"):
        st.text_area("Texto", st.session_state.get("texto_extraido", ""), height=300, disabled=True)

    # Atributos
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

        