import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np
import warnings
from datetime import datetime, timedelta
from auth_db import AuthDB

warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Análise - Projetos Corporativos MC Sonae",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

#=========== AUTHENTICATION SYSTEM ===========

# Inicializar banco de dados de autenticação
auth_db = AuthDB()

# Inicializar estado da sessão
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def login_page():
    """Página de login"""
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>🔐 Sistema de Login</h1>
            <h3>Dashboard de Análise - FadoLab</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        
        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                if username and password:
                    user = auth_db.autenticar(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user
                        st.success(f"✅ Bem-vindo, {user['nome_completo']}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos!")
                else:
                    st.warning("⚠️ Por favor, preencha todos os campos.")
        
        st.divider()
        
        with st.expander("ℹ️ Informações de Acesso"):
            st.markdown("""
            **Usuários de Teste:**
            
            **Nível Estratégico (Visão Executiva):**
            - Usuário: `admin` | Senha: `admin123`
            
            **Nível Tático (Gestão):**
            - Usuário: `gerente` | Senha: `gerente123`
            
            **Nível Operacional (Execução):**
            - Usuário: `operador` | Senha: `operador123`
            """)

def logout():
    """Função de logout"""
    auth_db.registrar_acao(st.session_state.user_info['username'], 'LOGOUT')
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()

def check_access_level(required_levels):
    """Verifica se o usuário tem o nível de acesso necessário"""
    if not st.session_state.authenticated:
        return False
    
    user_level = st.session_state.user_info['nivel_acesso']
    
    # Estratégico tem acesso a tudo
    if user_level == 'Estratégico':
        return True
    
    # Tático tem acesso a Tático e Operacional
    if user_level == 'Tático' and required_levels in ['Tático', 'Operacional']:
        return True
    
    # Operacional só tem acesso a Operacional
    if user_level == 'Operacional' and required_levels == 'Operacional':
        return True
    
    return False

# Verificar autenticação
if not st.session_state.authenticated:
    login_page()
    st.stop()

#=========== FUNCTIONS AND DATA LOADING ===========

@st.cache_data
def load_data(file_path):
    """Carrega dados do arquivo parquet"""
    import os
    
    # Tentar diferentes caminhos
    possible_paths = [
        file_path,  # Caminho relativo padrão
        os.path.join(os.path.dirname(__file__), file_path),  # Relativo ao script
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "datamart", "Relatorio_projetos_expandido_dados.parquet"),  # Absoluto do projeto
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_parquet(path)
            return df
    
    # Se não encontrar, mostrar erro mais informativo
    st.error(f"❌ Arquivo de dados não encontrado. Tentou nos caminhos: {possible_paths}")
    st.stop()

def create_grant(df):
    fig = px.timeline(df, x_start="Data_Inicio", x_end="Data_Fim", y="Projeto",color="Status",hover_data=['Investimento (€)', 'Progresso (%)', 'Responsavel'],title="Timeline dos Projetos - Análise de Cronograma")
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(height=400, xaxis_title="Período", yaxis_title="Projetos")
    
    st.plotly_chart(fig)

def create_deadline_analysis(df):
    df['Dias_Restantes'] = (df['Data_Fim'] - pd.Timestamp.now()).dt.days
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=df['Dias_Restantes'], y=df['Progresso (%)'],text=df['Projeto'],mode='markers+text',textposition='top center',marker=dict(size=15, color='orange'),name='Deadline Analysis')
    )

    fig.update_layout(height=500,title_text="Análise de Deadline",xaxis_title="Dias até o Deadline",yaxis_title="Progresso (%)",template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

def create_ROI(df):
    df['ROI_Progresso'] = df['Progresso (%)'] / (df['Investimento (€)'] / 1000)  # Progresso por mil euros
    
    fig = go.Figure()

    fig.add_trace(
        go.Bar(x=df['Projeto'], y=df['ROI_Progresso'],text=df['ROI_Progresso'].round(2),textposition='outside',marker_color='purple',name='ROI Progresso')
    )

    fig.update_layout(title="ROI de Progresso por Projeto",xaxis_title="Projeto",yaxis_title="ROI Progresso",height=500,template="plotly_white")

    st.plotly_chart(fig)

#=========== HEADER AND TITLE SECTION ===========

# Cabeçalho com informações do usuário
col1, col2 = st.columns([3, 1])

with col1:
    st.title("📊 Dashboard de Análise - Projetos Corporativos MC Sonae 2025")

with col2:
    st.markdown(f"""
    <div style='text-align: right; padding: 10px;'>
        <strong>👤 {st.session_state.user_info['nome_completo']}</strong><br>
        <span style='color: #666;'>🔑 {st.session_state.user_info['nivel_acesso']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sair", use_container_width=True):
        logout()

# Badge de nível de acesso
nivel_acesso = st.session_state.user_info['nivel_acesso']
if nivel_acesso == 'Estratégico':
    st.info("🎯 **Nível de Acesso:** Estratégico - Visão Executiva Completa")
elif nivel_acesso == 'Tático':
    st.info("⚙️ **Nível de Acesso:** Tático - Gestão e Coordenação")
else:
    st.info("🔧 **Nível de Acesso:** Operacional - Execução e Detalhamento")

# Badge com informação de filtros (será preenchido após aplicar filtros)
filtros_placeholder = st.empty()

st.divider()

#=========== DATA LOADING AND PREPARATION ===========

# Carregamento de dados expandidos
# Tentar primeiro o caminho local (para Streamlit Cloud)
try:
    df_original = load_data("Relatorio_projetos_expandido_dados.parquet")
except:
    # Fallback para estrutura local de desenvolvimento
    df_original = load_data("../data/datamart/Relatorio_projetos_expandido_dados.parquet")

#=========== SIDEBAR - FILTROS ===========

st.sidebar.header("🔍 Filtros")
st.sidebar.markdown("Utilize os filtros abaixo para personalizar a visualização dos dados.")

# Filtro de Departamento
departamento_selecionado = st.sidebar.multiselect(
    "Departamento",
    options=sorted(df_original['Departamento'].unique().tolist()),
    default=[]
)

# Filtro de Status
status_selecionado = st.sidebar.multiselect(
    "Status do Projeto",
    options=sorted(df_original['Status'].unique().tolist()),
    default=[]
)

# Filtro de Responsável
responsavel_selecionado = st.sidebar.multiselect(
    "Responsável",
    options=sorted(df_original['Responsavel'].unique().tolist()),
    default=[]
)

# Filtro de Investimento (Range Slider)
investimento_min = float(df_original['Investimento (€)'].min())
investimento_max = float(df_original['Investimento (€)'].max())
investimento_range = st.sidebar.slider(
    "Investimento (€)",
    min_value=investimento_min,
    max_value=investimento_max,
    value=(investimento_min, investimento_max),
    step=5000.0,
    format="€%.0f"
)

# Filtro de Progresso (Range Slider)
progresso_range = st.sidebar.slider(
    "Progresso (%)",
    min_value=0,
    max_value=100,
    value=(0, 100),
    step=5
)

# Filtro de Data
st.sidebar.subheader("📅 Período")
data_inicio_min = df_original['Data_Inicio'].min().date()
data_inicio_max = df_original['Data_Inicio'].max().date()

col1, col2 = st.sidebar.columns(2)
with col1:
    data_filtro_inicio = st.date_input(
        "Início",
        value=data_inicio_min,
        min_value=data_inicio_min,
        max_value=data_inicio_max
    )
with col2:
    data_filtro_fim = st.date_input(
        "Fim",
        value=data_inicio_max,
        min_value=data_inicio_min,
        max_value=data_inicio_max
    )

# Aplicar filtros
df = df_original.copy()

if departamento_selecionado:
    df = df[df['Departamento'].isin(departamento_selecionado)]

if status_selecionado:
    df = df[df['Status'].isin(status_selecionado)]

if responsavel_selecionado:
    df = df[df['Responsavel'].isin(responsavel_selecionado)]

df = df[
    (df['Investimento (€)'] >= investimento_range[0]) &
    (df['Investimento (€)'] <= investimento_range[1])
]

df = df[
    (df['Progresso (%)'] >= progresso_range[0]) &
    (df['Progresso (%)'] <= progresso_range[1])
]

df = df[
    (df['Data_Inicio'].dt.date >= data_filtro_inicio) &
    (df['Data_Inicio'].dt.date <= data_filtro_fim)
]

# Botão para limpar filtros
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Limpar Todos os Filtros"):
    st.rerun()

# Mostrar informações de filtros aplicados
st.sidebar.markdown("---")
st.sidebar.metric("Projetos Filtrados", len(df))
st.sidebar.metric("Total de Projetos", len(df_original))

# Mostrar porcentagem filtrada
percentual_filtrado = (len(df) / len(df_original)) * 100
st.sidebar.progress(percentual_filtrado / 100)
st.sidebar.caption(f"{percentual_filtrado:.1f}% dos projetos visíveis")

# Exibir resumo de filtros ativos
filtros_ativos = []
if len(departamento_selecionado) < len(df_original['Departamento'].unique()):
    filtros_ativos.append(f"Departamentos: {len(departamento_selecionado)}")
if len(status_selecionado) < len(df_original['Status'].unique()):
    filtros_ativos.append(f"Status: {len(status_selecionado)}")
if len(responsavel_selecionado) < len(df_original['Responsavel'].unique()):
    filtros_ativos.append(f"Responsáveis: {len(responsavel_selecionado)}")
if investimento_range != (investimento_min, investimento_max):
    filtros_ativos.append(f"Investimento: €{investimento_range[0]:,.0f} - €{investimento_range[1]:,.0f}")
if progresso_range != (0, 100):
    filtros_ativos.append(f"Progresso: {progresso_range[0]}% - {progresso_range[1]}%")

if filtros_ativos:
    filtros_placeholder.info(f"🔍 **Filtros Ativos:** {' | '.join(filtros_ativos)}")
else:
    filtros_placeholder.success("✅ Exibindo todos os projetos (sem filtros aplicados)")

if len(df) == 0:
    st.warning("⚠️ Nenhum projeto encontrado com os filtros selecionados. Ajuste os filtros.")
    st.stop()

# Preparação dos dados - criar colunas calculadas
df["Duracao_meses"] = ((df["Data_Fim"] - df["Data_Inicio"]).dt.days / 30.44).round(1)
df['ROI_Eficiencia'] = df['Progresso (%)'] / (df['Investimento (€)'] / 1000)

#=========== VISÃO ESTRATÉGICA ===========

if check_access_level('Estratégico'):
    st.header("🎯 VISÃO ESTRATÉGICA - KPIs Executivos")
    
    # Métricas estratégicas
    st.subheader("📈 Indicadores Estratégicos")
    
    # Calcular métricas principais
    total_investimento = df['Investimento (€)'].sum()
    progresso_medio = df['Progresso (%)'].mean()
    projetos_concluidos = len(df[df['Progresso (%)'] == 100])
    total_projetos = len(df)

    # Calcular ROI médio (já criado na preparação dos dados)
    roi_medio = df['ROI_Eficiencia'].mean()

    # Métricas principais em colunas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # KPI: Investimento Total
        st.metric(
            label="💰 Investimento Total",
            value=f"€{total_investimento:,.0f}",
            delta=f"Média: €{df['Investimento (€)'].mean():,.0f}"
        )

    with col2:
        # KPI: Progresso Médio
        delta_progresso = progresso_medio - 75  # Comparar com meta de 75%
        st.metric(
            label="📊 Progresso Médio",
            value=f"{progresso_medio:.1f}%",
            delta=f"{delta_progresso:+.1f}% vs meta"
        )

    with col3:
        # KPI: Projetos Concluídos
        taxa_conclusao = (projetos_concluidos / total_projetos) * 100
        st.metric(
            label="✅ Projetos Concluídos", 
            value=f"{projetos_concluidos}/{total_projetos}",
            delta=f"Taxa: {taxa_conclusao:.1f}%"
        )

    with col4:
        # KPI: ROI Médio (Eficiência)
        st.metric(
            label="📈 Eficiência Média",
            value=f"{roi_medio:.2f}",
            delta="Progresso/€1K investido"
        )
    
    st.markdown("---")
    
    # Distribuição estratégica por departamento
    st.subheader("💼 Visão Consolidada por Departamento")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Investimentos por departamento
        dept_invest = df.groupby('Departamento')['Investimento (€)'].sum().sort_values(ascending=False)
        
        fig = go.Figure(
            go.Pie(
                labels=dept_invest.index,
                values=dept_invest.values,
                textinfo='label+percent',
                name="Por Departamento",
                hole=0.4
            )
        )
        fig.update_layout(title="Distribuição de Investimentos", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_b:
        # Performance por departamento
        dept_performance = df.groupby('Departamento').agg({
            'Progresso (%)': 'mean',
            'ROI_Eficiencia': 'mean'
        }).round(2)
        
        st.markdown("**Performance por Departamento**")
        st.dataframe(dept_performance, use_container_width=True)
    
    # Insights Estratégicos
    st.subheader("💡 Insights Estratégicos")
    
    col_i1, col_i2 = st.columns(2)
    
    with col_i1:
        st.metric("🏆 Departamento Mais Eficiente", 
                 df.groupby('Departamento')['ROI_Eficiencia'].mean().idxmax(),
                 f"{df.groupby('Departamento')['ROI_Eficiencia'].mean().max():.2f}")
    
    with col_i2:
        st.metric("💰 Maior Investimento", 
                 df.groupby('Departamento')['Investimento (€)'].sum().idxmax(),
                 f"€{df.groupby('Departamento')['Investimento (€)'].sum().max():,.0f}")

    st.divider()

#=========== VISÃO TÁTICA ===========

if check_access_level('Tático'):
    st.header("⚙️ VISÃO TÁTICA - Gestão e Coordenação")
    
    st.subheader("📊 Análise Comparativa e Correlações")

    # Análise Bivariada - Correlações
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Investimento vs Progresso")
        # Scatter plot: Investimento x Progresso
        fig = px.scatter(df,
                         x = df['Investimento (€)'],
                         y = df['Progresso (%)'],
                         text=df['Projeto'],
                         color=df['Projeto']
                         )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Duração vs Progresso")  
        # Scatter plot: Duração x Progresso
        fig = px.scatter(df,
                         x = df['Duracao_meses'],
                         y = df['Progresso (%)'],
                         text=df['Projeto'],
                         color=df['Projeto']
                         )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Timeline dos Projetos")
        # Gráfico de barras horizontais (duração)
        fig = px.bar(df,
                    x = df['Duracao_meses'],
                    y = df['Projeto'],
                    orientation='h',
                    text=df['Duracao_meses'].apply(lambda x: f"{x:.1f}m"),
                    text_auto=True,
                    range_color='lightgreen'
                )
        
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Investimento por Status")
        # Box plot: Investimento agrupado por Status
        fig = px.box(df,
                     x = df['Investimento (€)'],
                     y = df['Status'],
                     color="Projeto",
                     points="all"
                     )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Matriz de Correlações
    st.subheader("📈 Matriz de Correlações")
    
    numeric_cols = ['Investimento (€)', 'Progresso (%)', 'Duracao_meses', 'ROI_Eficiencia']
    correlation_matrix = df[numeric_cols].corr()
    
    fig = px.imshow(
        correlation_matrix,
        text_auto='.3f',
        title="Correlação entre Variáveis",
        color_continuous_scale='RdBu_r',
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Ranking de Performance
    st.subheader("🏆 Ranking de Performance")
    
    ranking_df = df[['Projeto', 'Departamento', 'Investimento (€)', 'Progresso (%)', 'ROI_Eficiencia', 'Status']].copy()
    ranking_df = ranking_df.sort_values('ROI_Eficiencia', ascending=False)
    ranking_df['Posição'] = range(1, len(ranking_df) + 1)
    ranking_df = ranking_df[['Posição', 'Projeto', 'Departamento', 'ROI_Eficiencia', 'Progresso (%)', 'Investimento (€)', 'Status']]
    
    st.dataframe(ranking_df.head(10), use_container_width=True)

    st.divider()

#=========== VISÃO OPERACIONAL ===========

if check_access_level('Operacional'):
    st.header("🔧 VISÃO OPERACIONAL - Execução e Detalhamento")
    
    st.subheader("⏰ Cronograma e Timeline dos Projetos")

    create_grant(df)

    # Layout em colunas para análises operacionais
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Eficiência: Progresso por €1000")
        create_ROI(df)

    with col2:
        st.subheader("Análise de Deadline")
        create_deadline_analysis(df)
    
    # Análise Univariada Detalhada
    st.subheader("📊 Distribuições e Frequências Detalhadas")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Distribuição de Investimentos**")
        fig = go.Figure(
            go.Bar(
                x=df['Projeto'], 
                y=df['Investimento (€)'],
                text=df['Investimento (€)'].apply(lambda x: f'€{x:,.0f}'),
                textposition='outside',
                marker_color='#143982',
                name='Investimento'
            )
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_b:
        st.markdown("**Status dos Projetos**")
        status_counts = df['Status'].value_counts()
        fig = go.Figure(
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                textinfo='label+value',
                name="Status"
            )
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

#=========== DETAILED STATISTICS SECTION ===========

if check_access_level('Operacional'):
    st.header("📋 Estatísticas Detalhadas e Insights")

    # Tabs para organizar informações estatísticas
    tab1, tab2, tab3 = st.tabs(["📊 Estatísticas Descritivas", "🔍 Análise de Correlação", "🎯 Insights e Recomendações"])

    with tab1:
        st.subheader("📊 Estatísticas Descritivas Consolidadas")
    
        # Estatísticas descritivas das variáveis numéricas
        st.write("**Resumo Estatístico dos Dados:**")
        stats_cols = ['Investimento (€)', 'Progresso (%)', 'Duracao_meses', 'ROI_Eficiencia']
        
        # Criar DataFrame com estatísticas
        stats_summary = df[stats_cols].describe().round(2)
        st.dataframe(stats_summary, use_container_width=True)
        
        st.subheader("🏆 Ranking de Performance")
        
        # Ranking baseado na eficiência (ROI_Eficiencia)
        ranking_df = df[['Projeto', 'Departamento', 'Investimento (€)', 'Progresso (%)', 'ROI_Eficiencia', 'Status']].copy()
        ranking_df = ranking_df.sort_values('ROI_Eficiencia', ascending=False)
        ranking_df['Posição'] = range(1, len(ranking_df) + 1)
        
        # Reordenar colunas
        ranking_df = ranking_df[['Posição', 'Projeto', 'Departamento', 'ROI_Eficiencia', 'Progresso (%)', 'Investimento (€)', 'Status']]
        
        st.dataframe(ranking_df, use_container_width=True)

    with tab2:
        st.subheader("📈 Matriz de Correlação Completa")
        
        # Matriz de correlação
        numeric_cols = ['Investimento (€)', 'Progresso (%)', 'Duracao_meses', 'ROI_Eficiencia']
        correlation_matrix = df[numeric_cols].corr()
        
        # Heatmap de correlações
        fig = px.imshow(
            correlation_matrix,
            text_auto='.3f',
            title="Matriz de Correlação entre Variáveis",
            color_continuous_scale='RdBu_r',
            aspect="auto"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de correlações
        st.write("**Coeficientes de Correlação:**")
        st.dataframe(correlation_matrix.round(3), use_container_width=True)
        
        st.subheader("📊 Análise de Variabilidade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Box plot do investimento por departamento
            fig = px.box(df, x='Departamento', y='Investimento (€)', 
                        title="Variabilidade do Investimento por Departamento")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot do progresso por status
            fig = px.box(df, x='Status', y='Progresso (%)', 
                        title="Variabilidade do Progresso por Status")
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("🔍 Principais Achados")
        
        # Calcular métricas para insights
        total_investimento = df['Investimento (€)'].sum()
        progresso_medio = df['Progresso (%)'].mean()
        projetos_concluidos = len(df[df['Progresso (%)'] == 100])
        total_projetos = len(df)
        
        # Análise automática dos dados
        total_investimento_formatted = f"€{total_investimento:,.0f}"
        melhor_projeto = ranking_df.iloc[0]['Projeto']
        pior_projeto = ranking_df.iloc[-1]['Projeto']
        correlacao_inv_prog = correlation_matrix.loc['Investimento (€)', 'Progresso (%)']
        
        findings = [
            f"💰 **Investimento Total**: {total_investimento_formatted} distribuídos em {total_projetos} projetos",
            f"📊 **Progresso Médio**: {progresso_medio:.1f}% com {projetos_concluidos} projetos concluídos",
            f"🏆 **Melhor Performance**: {melhor_projeto} (maior eficiência)",
            f"⚠️ **Menor Performance**: {pior_projeto} (menor eficiência)",
            f"🔗 **Correlação Investimento-Progresso**: {correlacao_inv_prog:.3f} ({'Positiva' if correlacao_inv_prog > 0 else 'Negativa'})",
            f"⏱️ **Duração Média dos Projetos**: {df['Duracao_meses'].mean():.1f} meses"
        ]
        
        for finding in findings:
            st.markdown(f"• {finding}")
        
        st.subheader("💡 Recomendações Estratégicas")
        
        recommendations = []
        
        # Recomendações baseadas na análise
        if progresso_medio < 75:
            recommendations.append("🎯 **Acelerar Projetos**: Progresso médio abaixo da meta (75%). Revisar cronogramas.")
        
        if correlacao_inv_prog < 0.3:
            recommendations.append("💰 **Otimizar Investimentos**: Baixa correlação entre investimento e progresso. Revisar alocação de recursos.")
        
        projetos_atrasados = len(df[df['Progresso (%)'] < 50])
        if projetos_atrasados > 0:
            recommendations.append(f"⚠️ **Atenção Especial**: {projetos_atrasados} projeto(s) com progresso crítico (<50%). Intervenção necessária.")
        
        # Análise por departamento
        dept_performance = df.groupby('Departamento')['ROI_Eficiencia'].mean().sort_values(ascending=False)
        melhor_dept = dept_performance.index[0]
        recommendations.append(f"🏆 **Benchmark Departamental**: {melhor_dept} apresenta melhor eficiência. Compartilhar boas práticas.")
        
        if not recommendations:
            recommendations.append("✅ **Performance Satisfatória**: Todos os indicadores estão dentro dos parâmetros aceitáveis.")
        
        for rec in recommendations:
            st.markdown(f"• {rec}")
        
        st.subheader("📊 Indicadores de Gestão")
        
        # Calcular métricas necessárias
        taxa_conclusao = (projetos_concluidos / total_projetos) * 100
        roi_medio = df['ROI_Eficiencia'].mean()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Taxa de Conclusão", f"{taxa_conclusao:.1f}%")
            st.metric("Projetos Críticos", f"{len(df[df['Progresso (%)'] < 50])}")
        
        with col2:
            st.metric("Eficiência Média", f"{roi_medio:.2f}")
            st.metric("Desvio Padrão ROI", f"{df['ROI_Eficiencia'].std():.2f}")
        
        with col3:
            st.metric("Investimento Médio", f"€{df['Investimento (€)'].mean():,.0f}")
            st.metric("Duração Média", f"{df['Duracao_meses'].mean():.1f}m")

#=========== FOOTER AND METADATA SECTION ===========

st.markdown("---")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown(f"""
    **👤 Usuário:** {st.session_state.user_info['nome_completo']}  
    **🔑 Nível:** {st.session_state.user_info['nivel_acesso']}
    """)

with col_f2:
    st.markdown("""
    **📊 Dashboard FADOLAB**  
    *Análise Exploratória de Dados*
    """)

with col_f3:
    st.markdown("""
    **🛠️ Tecnologias:**  
    Streamlit | Plotly | SQLite
    """)

st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <em>Desenvolvido com Streamlit | Dados atualizados em tempo real | Sistema de Autenticação SQLite</em>
</div>
""", unsafe_allow_html=True)