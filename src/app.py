import streamlit as st
import pandas as pd
import altair as alt
from src.services.dashboard_service import DashboardService
from src.data.quality_service import DataQualityEngine

# Configuração da página e layout
st.set_page_config(
    page_title="PEDFOR - Dashboard de Matrículas e Frequência",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (Glassmorphism & Dark Mode)
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .kpi-card-box {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .kpi-title { font-size: 0.82rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
    .kpi-val { font-size: 1.75rem; font-weight: 700; color: #ffffff; }
    .kpi-sub { font-size: 0.78rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 1. CABEÇALHO DO DASHBOARD
st.title("🎓 Dashboard de Matrículas, Cursistas e Frequência - PEDFOR")
st.caption("Consulta unificada SERE / PEDFOR | Filtros por Turma, Formador, NRE, Período, Dia da Semana e Situação do Cursista")

# Carregar lista base para filtros
base_cursistas = DashboardService.get_cursistas()

# 2. FILTROS NA SIDEBAR
st.sidebar.header("🔍 Filtros Avançados de Busca")

nres_list = ["Todos"] + sorted(list(set(r["nre"] for r in base_cursistas if r.get("nre"))))
filtro_nre = st.sidebar.selectbox("Núcleo Regional (NRE):", nres_list)

formadores_list = ["Todos"] + sorted(list(set(r["turma_formador"] for r in base_cursistas if r.get("turma_formador"))))
filtro_formador = st.sidebar.selectbox("Formador / Tutora:", formadores_list)

turmas_list = ["Todas"] + sorted(list(set(r["turma_nome"] for r in base_cursistas if r.get("turma_nome"))))
filtro_turma = st.sidebar.selectbox("Turma:", turmas_list)

filtro_situacao = st.sidebar.selectbox("Status do Cursista:", ["Todas", "Matriculado", "Remanejado", "Desistente"])
filtro_turno = st.sidebar.selectbox("Período / Turno:", ["Todos", "Manhã", "Tarde", "Noite"])
filtro_dia = st.sidebar.selectbox("Dia da Semana:", ["Todos", "SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA"])

# Dicionário de filtros para o serviço
filters_dict = {
    "nre": filtro_nre,
    "formador": filtro_formador,
    "turma_nome": filtro_turma,
    "situacao": filtro_situacao,
    "periodo_turno": filtro_turno,
    "dia_semana": filtro_dia
}

# 3. CARREGAMENTO DOS DADOS COM TRATAMENTO DE ESTADOS DE INTERFACE
with st.spinner("Consultando dados de cursistas e turmas..."):
    kpis = DashboardService.get_kpis(filters_dict)
    cursistas_filtrados = DashboardService.get_cursistas(filters_dict)
    formadores_ranking = DashboardService.get_cursistas_por_formador(filters_dict)

if not kpis:
    st.error("⚠️ Ocorreu um erro ao carregar o dashboard. Tente novamente.")
    st.stop()

# 4. CARDS DE KPI (Estado Success)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Total Cursistas</div>
            <div class="kpi-val">{kpis['total_inscritos']:,}</div>
            <div class="kpi-sub" style="color: #6366f1;">Inscrições no Filtro</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Matriculados</div>
            <div class="kpi-val">{kpis['total_matriculados']:,}</div>
            <div class="kpi-sub" style="color: #10b981;">Ativos na Turma</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Remanejados</div>
            <div class="kpi-val">{kpis['total_remanejados']}</div>
            <div class="kpi-sub" style="color: #f59e0b;">Transferidos</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Desistentes</div>
            <div class="kpi-val">{kpis['total_desistentes']}</div>
            <div class="kpi-sub" style="color: #f43f5e;">Cancelamentos</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Frequência Média</div>
            <div class="kpi-val">{kpis['frequencia_media_pct']}%</div>
            <div class="kpi-sub" style="color: #06b6d4;">Média de Presença</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 5. GRÁFICOS E VISUALIZAÇÕES
c_g1, c_g2 = st.columns([1, 1])

with c_g1:
    st.subheader("📊 Status do Cursista na Turma")
    if cursistas_filtrados:
        df_curr = pd.DataFrame(cursistas_filtrados)
        sit_counts = df_curr["situacao"].value_counts().reset_index()
        sit_counts.columns = ["Status", "Quantidade"]
        
        donut = alt.Chart(sit_counts).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Quantidade", type="quantitative"),
            color=alt.Color(field="Status", type="nominal", scale=alt.Scale(range=['#10b981', '#f59e0b', '#f43f5e'])),
            tooltip=['Status', 'Quantidade']
        ).properties(height=300)
        st.altair_chart(donut, use_container_width=True)
    else:
        st.info("Nenhum registro para exibir no gráfico.")

with c_g2:
    st.subheader("👥 Total de Cursistas por Formador / Tutora")
    if formadores_ranking:
        df_rank = pd.DataFrame(formadores_ranking[:10])
        bar_chart = alt.Chart(df_rank).mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6, color='#6366f1').encode(
            x=alt.X('total_cursistas:Q', title='Total de Cursistas'),
            y=alt.Y('formador:N', title='Formador / Tutora', sort='-x'),
            tooltip=['formador', 'total_cursistas', 'matriculados', 'remanejados', 'desistentes']
        ).properties(height=300)
        st.altair_chart(bar_chart, use_container_width=True)

st.markdown("---")

# 6. TABELA DE CONSULTA DE CURSISTAS & ESTADO VAZIO
st.subheader("📋 Consulta e Informações dos Cursistas")

search_text = st.text_input("🔎 Pesquisar por Nome do Cursista, CGM, E-mail ou Turma:", "")
if search_text:
    filters_dict["search"] = search_text
    cursistas_filtrados = DashboardService.get_cursistas(filters_dict)

if cursistas_filtrados:
    df_tabela = pd.DataFrame(cursistas_filtrados)
    df_tabela = df_tabela[["cgm", "cursista_nome", "cursista_email", "nre", "turma_nome", "turma_formador", "turma_dia", "turma_horario", "situacao", "frequencia_pct"]]
    df_tabela.columns = ["CGM", "Nome do Cursista", "E-mail Institucional", "NRE", "Turma", "Formador / Tutora", "Dia da Semana", "Horário / Turno", "Status na Turma", "Frequência (%)"]
    
    st.dataframe(
        df_tabela.style.highlight_between(left=0, right=74.9, subset=["Frequência (%)"], color="rgba(244, 63, 94, 0.2)"),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Mostrando {len(df_tabela):,} cursistas correspondentes ao filtro.")
else:
    # Estado Vazio
    st.warning("⚠️ Nenhum cursista encontrado para os critérios de busca selecionados.")

st.markdown("---")

# 7. SEÇÃO DE ATUALIZAÇÃO DE FREQUÊNCIA (REQUISITO EXPLÍCITO)
st.subheader("✏️ Atualização de Frequência do Cursista")

col_f1, col_f2, col_f3 = st.columns([2, 1, 1])

with col_f1:
    cgm_input = st.text_input("Informe o CGM ou E-mail do cursista para atualização:", "")

with col_f2:
    nova_freq = st.number_input("Nova Frequência (%):", min_value=0.0, max_value=100.0, value=100.0, step=5.0)

with col_f3:
    st.write(" ")
    st.write(" ")
    if st.button("💾 Atualizar Frequência", use_container_width=True):
        if cgm_input:
            sucesso = DashboardService.update_frequencia(cgm_input.strip(), nova_freq)
            if sucesso:
                st.success(f"✅ Frequência do cursista {cgm_input} atualizada com sucesso para {nova_freq}%!")
                st.rerun()
            else:
                st.error(f"❌ Cursista com CGM/E-mail '{cgm_input}' não foi localizado.")
        else:
            st.warning("Por favor digite o CGM ou E-mail do cursista.")

# 8. PAINEL DE AUDITORIA DE QUALIDADE
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Auditoria de Qualidade de Dados")
audit = DataQualityEngine.audit_dataset(base_cursistas)
st.sidebar.metric("Data Quality Score", f"{audit['quality_score']}%", delta="Excelente" if audit['quality_score'] >= 95 else "Atenção")
st.sidebar.caption(f"Total Registros: {audit['total_records']} | NREs: {len(nres_list)-1} | Duplicados: {audit['duplicate_count']}")
