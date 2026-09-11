import streamlit as st
import pandas as pd
import altair as alt
from src.services.dashboard_service import DashboardService
from src.data.quality_service import DataQualityEngine

# Configuração da página e layout
st.set_page_config(
    page_title="PEDFOR Dashboard - Novo Dashboard",
    page_icon="📊",
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
st.title("📊 Dashboard Executivo - PEDFOR")
st.caption("Visão Geral de Desempenho, Atendimentos e Indicadores do Sistema | Banco de Dados: TiDB Cloud (SQL)")

# Sidebar - Filtros Globais
st.sidebar.header("🔍 Filtros do Dashboard")
filtro_unidade = st.sidebar.selectbox("Regional / Unidade:", ["Todas", "Curitiba Central", "Londrina", "Maringá", "Cascavel", "Ponta Grossa"])
filtro_status = st.sidebar.multiselect("Status do Pedido:", ["concluido", "em_andamento", "pendente", "cancelado"], default=["concluido", "em_andamento", "pendente"])
data_inicio = st.sidebar.date_input("Data Início:", pd.to_datetime("2026-01-01"))
data_fim = st.sidebar.date_input("Data Fim:", pd.to_datetime("2026-12-31"))

# 2. CARREGAMENTO DOS DADOS (Com simulação dos 4 Estados de Interface)
with st.spinner("Carregando indicadores do TiDB..."):
    kpis_data = DashboardService.get_kpis()
    series_data = DashboardService.get_series()
    tabela_data = DashboardService.get_tabela()

# Estado de Erro Trado
if not kpis_data:
    st.error("⚠️ Ocorreu um erro ao consultar os dados no servidor. Por favor tente novamente.")
    st.stop()

# 3. SEÇÃO DE CARDS KPI (Sucesso)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Total de Pedidos</div>
            <div class="kpi-val">{kpis_data['total_registros']:,}</div>
            <div class="kpi-sub">↑ 12.4% vs mês anterior</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Concluídos</div>
            <div class="kpi-val">{kpis_data['total_concluidos']:,}</div>
            <div class="kpi-sub" style="color: #10b981;">{kpis_data['taxa_conclusao_pct']}% Eficiência</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Em Andamento</div>
            <div class="kpi-val">{kpis_data['total_em_andamento']:,}</div>
            <div class="kpi-sub" style="color: #f59e0b;">{kpis_data['total_pendentes']} Pendentes</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Montante Financeiro</div>
            <div class="kpi-val">R$ {kpis_data['valor_total']:,.2f}</div>
            <div class="kpi-sub">Total Acumulado</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-title">Valor Médio</div>
            <div class="kpi-val">R$ {kpis_data['valor_medio']:,.2f}</div>
            <div class="kpi-sub">Por Atendimento</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 4. GRÁFICOS E VISUALIZAÇÕES
c_chart1, c_chart2 = st.columns([2, 1])

with c_chart1:
    st.subheader("📈 Evolução Temporal dos Atendimentos")
    if series_data:
        df_series = pd.DataFrame(series_data)
        chart = alt.Chart(df_series).mark_area(
            line={'color':'#6366f1'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#6366f1', offset=0),
                       alt.GradientStop(color='rgba(99, 102, 241, 0.05)', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X('mes_ano:N', title='Mês/Ano'),
            y=alt.Y('total_pedidos:Q', title='Quantidade de Pedidos'),
            tooltip=['mes_ano', 'total_pedidos', 'concluidos', 'montante_financeiro']
        ).properties(height=320)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o período selecionado.")

with c_chart2:
    st.subheader("🍩 Distribuição por Status")
    status_df = pd.DataFrame([
        {"Status": "Concluídos", "Quantidade": kpis_data["total_concluidos"]},
        {"Status": "Em Andamento", "Quantidade": kpis_data["total_em_andamento"]},
        {"Status": "Pendentes", "Quantidade": kpis_data["total_pendentes"]},
        {"Status": "Cancelados", "Quantidade": kpis_data["total_cancelados"]}
    ])
    donut = alt.Chart(status_df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Quantidade", type="quantitative"),
        color=alt.Color(field="Status", type="nominal", scale=alt.Scale(range=['#10b981', '#6366f1', '#f59e0b', '#f43f5e'])),
        tooltip=['Status', 'Quantidade']
    ).properties(height=320)
    st.altair_chart(donut, use_container_width=True)

st.markdown("---")

# 5. TABELA RANKING POR UNIDADE & ESTADO VAZIO
st.subheader("🏆 Ranking de Eficiência por Regional / Unidade")
items = tabela_data.get("items", [])

if items:
    df_tabela = pd.DataFrame(items)
    df_tabela.columns = ["ID", "Unidade / Regional", "UF", "Total Atendimentos", "Concluídos", "Valor Total (R$)", "Eficiência (%)"]
    
    # Busca na tabela
    search_query = st.text_input("🔎 Pesquisar unidade:", "")
    if search_query:
        df_tabela = df_tabela[df_tabela["Unidade / Regional"].str.contains(search_query, case=False)]

    if len(df_tabela) == 0:
        st.warning("⚠️ Nenhum registro encontrado para a busca especificada.")
    else:
        st.dataframe(
            df_tabela.style.highlight_max(axis=0, subset=["Eficiência (%)"], color="rgba(16, 185, 129, 0.2)"),
            use_container_width=True,
            hide_index=True
        )
else:
    # Estado Vazio
    st.info("ℹ️ Nenhum dado cadastrado para exibição na tabela.")

# 6. PAINEL DE QUALIDADE DE DADOS
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Qualidade de Dados")
audit = DataQualityEngine.audit_dataset(items if items else [])
st.sidebar.metric("Data Quality Score", f"{audit['quality_score']}%", delta="Excelente" if audit['quality_score'] >= 95 else "Atenção")
st.sidebar.caption(f"Registros Auditados: {audit['total_records']} | Duplicados: {audit['duplicate_count']}")
