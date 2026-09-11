import streamlit as st
import pandas as pd
import altair as alt
from src.services.dashboard_service import DashboardService
from src.data.quality_service import DataQualityEngine

# Configuração da página e layout
st.set_page_config(
    page_title="PEDFOR - Dashboard de Matrículas",
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
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .kpi-title { font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
    .kpi-val { font-size: 1.8rem; font-weight: 700; color: #ffffff; }
    .kpi-sub { font-size: 0.8rem; color: #10b981; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 1. CABEÇALHO DO DASHBOARD
st.title("🎓 Dashboard de Matrículas - PEDFOR")
st.caption("Acompanhamento de Inscrições, Turmas, Formadores e E-mails de Confirmação | Dados Integrados")

# Sidebar - Filtros Globais
st.sidebar.header("🔍 Filtros de Consulta")
formadores_list = ["Todos"] + sorted(list(set(r["turma_formador"] for r in DashboardService._load_json_data() if r.get("turma_formador"))))
filtro_formador = st.sidebar.selectbox("Formador Responsável:", formadores_list)
filtro_dia = st.sidebar.multiselect("Dia da Semana:", ["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA"], default=["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA"])
filtro_status_email = st.sidebar.radio("Status do E-mail:", ["Todos", "enviado", "pendente"])

# 2. CARREGAMENTO DOS DADOS (Com simulação dos 4 Estados de Interface)
with st.spinner("Carregando dados das matrículas..."):
    kpis = DashboardService.get_kpis()
    series = DashboardService.get_series()
    tabela = DashboardService.get_tabela_turmas()
    raw_data = DashboardService._load_json_data()

# Estado de Erro Trado
if not kpis:
    st.error("⚠️ Ocorreu um erro ao carregar os dados de matrículas. Por favor tente novamente.")
    st.stop()

# 3. SEÇÃO DE CARDS KPI (Sucesso)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Total de Matrículas</div>
            <div class="kpi-val">{kpis['total_matriculas']:,}</div>
            <div class="kpi-sub">Inscrições Realizadas</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Cursistas Únicos</div>
            <div class="kpi-val">{kpis['total_cursistas_unicos']:,}</div>
            <div class="kpi-sub" style="color: #6366f1;">Professores / Alunos</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Turmas Ocupadas</div>
            <div class="kpi-val">{kpis['total_turmas']}</div>
            <div class="kpi-sub" style="color: #f59e0b;">Turmas Ativas</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Formadores</div>
            <div class="kpi-val">{kpis['total_formadores']}</div>
            <div class="kpi-sub">Formadores Alocados</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">E-mails Enviados</div>
            <div class="kpi-val">{kpis['taxa_envio_email_pct']}%</div>
            <div class="kpi-sub" style="color: #10b981;">{kpis['emails_enviados']:,} Confirmações</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 4. GRÁFICOS DE MATRÍCULA
c_chart1, c_chart2 = st.columns([2, 1])

with c_chart1:
    st.subheader("📅 Distribuicão de Matrículas por Dia da Semana")
    if series:
        df_series = pd.DataFrame(series)
        chart = alt.Chart(df_series).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, color='#6366f1').encode(
            x=alt.X('dia_semana:N', title='Dia da Semana', sort=['SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA']),
            y=alt.Y('total_matriculas:Q', title='Total de Cursistas Matriculados'),
            tooltip=['dia_semana', 'total_matriculas']
        ).properties(height=320)
        st.altair_chart(chart, use_container_width=True)

with c_chart2:
    st.subheader("✉️ Status de Confirmação")
    status_df = pd.DataFrame([
        {"Status": "Enviado", "Quantidade": kpis["emails_enviados"]},
        {"Status": "Pendente", "Quantidade": kpis["emails_pendentes"]}
    ])
    donut = alt.Chart(status_df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Quantidade", type="quantitative"),
        color=alt.Color(field="Status", type="nominal", scale=alt.Scale(range=['#10b981', '#f59e0b'])),
        tooltip=['Status', 'Quantidade']
    ).properties(height=320)
    st.altair_chart(donut, use_container_width=True)

st.markdown("---")

# 5. TABELA DETALHADA DE TURMAS & FORMADORES
st.subheader("📚 Detalhamento das Turmas e Formadores")
items = tabela.get("items", [])

if items:
    df_tabela = pd.DataFrame(items)
    # Seleção e renomeação de colunas amigáveis
    df_tabela = df_tabela[["turma_nome", "turma_formador", "turma_dia", "turma_horario", "total_cursistas", "emails_enviados", "taxa_confirmacao_pct"]]
    df_tabela.columns = ["Nome da Turma", "Formador Responsável", "Dia da Semana", "Horário", "Total Cursistas", "E-mails Enviados", "Taxa Confirmação (%)"]
    
    # Filtro dinâmico por formador
    if filtro_formador != "Todos":
        df_tabela = df_tabela[df_tabela["Formador Responsável"] == filtro_formador]

    # Busca textual rápida
    search_query = st.text_input("🔎 Pesquisar por turma ou formador:", "")
    if search_query:
        df_tabela = df_tabela[
            df_tabela["Nome da Turma"].str.contains(search_query, case=False) |
            df_tabela["Formador Responsável"].str.contains(search_query, case=False)
        ]

    if len(df_tabela) == 0:
        st.warning("⚠️ Nenhuma turma encontrada para os filtros aplicados.")
    else:
        st.dataframe(
            df_tabela.style.highlight_max(axis=0, subset=["Total Cursistas"], color="rgba(99, 102, 241, 0.2)"),
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("ℹ️ Nenhum registro de turma cadastrado.")

# 6. PAINEL DE QUALIDADE DOS DADOS (Sidebar)
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Auditoria dos Dados")
audit = DataQualityEngine.audit_dataset(raw_data)
st.sidebar.metric("Data Quality Score", f"{audit['quality_score']}%", delta="Excelente" if audit['quality_score'] >= 95 else "Atenção")
st.sidebar.caption(f"Total Auditado: {audit['total_records']} matrículas | Duplicados: {audit['duplicate_count']}")
