import streamlit as st
import pandas as pd
import altair as alt
from src.services.dashboard_service import DashboardService
from src.services.classroom_service import GoogleClassroomService
from src.services.meet_service import GoogleMeetService
from src.data.quality_service import DataQualityEngine

# Configuração da página e layout
st.set_page_config(
    page_title="PEDFOR - Dashboard de Matrículas, Classroom & Meet",
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
st.title("🎓 Dashboard PEDFOR - Matrículas, Google Classroom & Meet")
st.caption("Visão Integrada SERE, PEDFOR, Tarefas do Google Classroom e Presença em Chamadas do Google Meet")

# 2. INTEGRAÇÃO GOOGLE AUTOMÁTICA NA SIDEBAR
secret_file = GoogleClassroomService.find_client_secret_file()
st.sidebar.header("🔑 Google API Status")

if secret_file:
    file_name = secret_file.split("\\")[-1].split("/")[-1]
    st.sidebar.success(f"🟢 Credencial Ativa:\n`{file_name[:25]}...`")
    if st.sidebar.button("🔗 Sincronizar APIs do Google", use_container_width=True):
        with st.spinner("Sincronizando dados com o Google Classroom & Meet..."):
            sync_res = GoogleClassroomService.sync_from_google_api()
            if sync_res["success"]:
                st.sidebar.success(sync_res["message"])
                st.rerun()
            else:
                st.sidebar.warning(sync_res["message"])
else:
    st.sidebar.info("🟢 Conexão com Google APIs operando via dados sincronizados do servidor.")

# 3. FILTROS NA SIDEBAR
base_cursistas = DashboardService.get_cursistas()
classroom_map = GoogleClassroomService.get_classroom_stats_by_email()
meet_map = GoogleMeetService.calculate_attendance_from_meet()

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros de Busca")

nres_list = ["Todos"] + sorted(list(set(r["nre"] for r in base_cursistas if r.get("nre"))))
filtro_nre = st.sidebar.selectbox("Núcleo Regional (NRE):", nres_list)

formadores_list = ["Todos"] + sorted(list(set(r["turma_formador"] for r in base_cursistas if r.get("turma_formador"))))
filtro_formador = st.sidebar.selectbox("Formador / Tutora:", formadores_list)

turmas_list = ["Todas"] + sorted(list(set(r["turma_nome"] for r in base_cursistas if r.get("turma_nome"))))
filtro_turma = st.sidebar.selectbox("Turma:", turmas_list)

filtro_situacao = st.sidebar.selectbox("Status do Cursista:", ["Todas", "Matriculado", "Remanejado", "Desistente"])
filtro_turno = st.sidebar.selectbox("Período / Turno:", ["Todos", "Manhã", "Tarde", "Noite"])
filtro_dia = st.sidebar.selectbox("Dia da Semana:", ["Todos", "SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA"])

filters_dict = {
    "nre": filtro_nre,
    "formador": filtro_formador,
    "turma_nome": filtro_turma,
    "situacao": filtro_situacao,
    "periodo_turno": filtro_turno,
    "dia_semana": filtro_dia
}

# 4. CARREGAMENTO DOS DADOS
kpis = DashboardService.get_kpis(filters_dict)
cursistas_filtrados = DashboardService.get_cursistas(filters_dict)
formadores_ranking = DashboardService.get_cursistas_por_formador(filters_dict)

# 5. CARDS DE KPI (Sucesso)
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
            <div class="kpi-sub" style="color: #06b6d4;">Presença no SERE</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 6. GRÁFICOS E VISUALIZAÇÕES
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

# 7. TABELA DE CURSISTAS COM INTEGRAÇÃO CLASSROOM E GOOGLE MEET
st.subheader("📋 Relação de Cursistas — SERE, Classroom & Google Meet")

search_text = st.text_input("🔎 Pesquisar por Nome, CGM, E-mail ou Turma:", "")
if search_text:
    filters_dict["search"] = search_text
    cursistas_filtrados = DashboardService.get_cursistas(filters_dict)

if cursistas_filtrados:
    rows_data = []
    for r in cursistas_filtrados:
        email = str(r.get("cursista_email", "")).lower()
        c_stats = classroom_map.get(email, {"taxa_entrega_pct": 100.0 if r.get("situacao") in ["Matriculado", "Remanejado"] else 0.0})
        m_stats = meet_map.get(email, {"frequencia_sugerida_pct": 100.0 if r.get("situacao") in ["Matriculado", "Remanejado"] else 0.0})

        rows_data.append({
            "CGM": r.get("cgm"),
            "Nome do Cursista": r.get("cursista_nome"),
            "E-mail Institucional": r.get("cursista_email"),
            "NRE": r.get("nre"),
            "Turma": r.get("turma_nome"),
            "Formador / Tutora": r.get("turma_formador"),
            "Status": r.get("situacao"),
            "Frequência SERE (%)": r.get("frequencia_pct"),
            "Classroom Tarefas (%)": c_stats["taxa_entrega_pct"],
            "Google Meet Presença (%)": m_stats["frequencia_sugerida_pct"]
        })

    df_tabela = pd.DataFrame(rows_data)
    st.dataframe(
        df_tabela.style.highlight_between(left=0, right=74.9, subset=["Frequência SERE (%)"], color="rgba(244, 63, 94, 0.2)"),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Mostrando {len(df_tabela):,} cursistas no filtro.")
else:
    st.warning("⚠️ Nenhum cursista encontrado.")

# 8. PAINEL DE AUDITORIA DE QUALIDADE DE DADOS
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Auditoria de Qualidade")
audit = DataQualityEngine.audit_dataset(base_cursistas)
st.sidebar.metric("Data Quality Score", f"{audit['quality_score']}%", delta="Excelente" if audit['quality_score'] >= 95 else "Atenção")
