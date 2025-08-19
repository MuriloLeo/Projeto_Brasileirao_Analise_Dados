import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Brasileirão (2012 - 2022)",
    page_icon="⚽",
    layout="wide",
)

# --- Carregamento dos dados ---
df_classificacao = pd.read_csv("classificacao_final_brasileirao.csv")
df_final = pd.read_csv("dashboard_brasileirao.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Temporada (apenas 1 temporada por vez)
anos_disponiveis = sorted(df_classificacao['Temporada'].unique())
ano_selecionado = st.sidebar.selectbox(
    "Temporada", anos_disponiveis, index=len(anos_disponiveis) - 1
)

# Filtro de Time (múltiplos times)
times_disponiveis = sorted(df_classificacao['Time'].unique())
times_selecionados = st.sidebar.multiselect(
    "Time", times_disponiveis, default=times_disponiveis
)

# Filtro de Rodada
rodadas_disponiveis = sorted(df_final[df_final['Temporada'] == ano_selecionado]['Rodada'].unique())
rodada_selecionada = st.sidebar.selectbox(
    "Rodada (Opcional)",
    ["Todas"] + rodadas_disponiveis,
    index=0
)

# --- Filtragem do DataFrame de Classificação ---
df_filtrado_classificacao = df_classificacao[
    (df_classificacao['Temporada'] == ano_selecionado) &
    (df_classificacao['Time'].isin(times_selecionados))
]

# --- Conteúdo Principal ---
st.title("⚽ Dashboard Brasileirão (2012 - 2022)")
st.markdown("Explore os dados relacionados com o Campeonato Brasileiro.")

# --- KPIs ---
if not df_filtrado_classificacao.empty:
    # Campeão (maior pontuação da temporada selecionada)
    campeao_time = df_filtrado_classificacao.loc[df_filtrado_classificacao['Pontos'].idxmax(), "Time"]

    # Filtrar apenas o campeão
    df_campeao = df_filtrado_classificacao[df_filtrado_classificacao["Time"] == campeao_time].iloc[0]

    # KPIs do campeão
    total_vitorias = df_campeao["Vitorias"]
    total_derrotas = df_campeao["Derrotas"]
    total_empates = df_campeao["Empates"]
    saldo_gols = df_campeao["Saldo_Gols"]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🏆 Campeão", campeao_time)
    col2.metric("✅ Vitórias", f"{total_vitorias}")
    col3.metric("❌ Derrotas", f"{total_derrotas}")
    col4.metric("🤝 Empates", f"{total_empates}")
    col5.metric("⚡ Saldo de Gols", f"{saldo_gols}")

st.markdown("---")

# --- Classificação Geral (Horizontal) ---
st.subheader(f"📊 Classificação {ano_selecionado}")

if not df_filtrado_classificacao.empty:
    classificacao = df_filtrado_classificacao.sort_values(by="Pontos", ascending=True)

    altura_classificacao = max(400, 25 * len(classificacao))  # dinâmico

    grafico_classificacao = px.bar(
        classificacao,
        x="Pontos",
        y="Time",
        text="Pontos",
        orientation="h",
        title=f"Classificação {ano_selecionado} (Pontos)",
        labels={"Pontos": "Total de Pontos", "Time": "Times"},
        height=altura_classificacao
    )

    grafico_classificacao.update_traces(textposition="outside")
    grafico_classificacao.update_layout(
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=120, r=20, t=50, b=50)
    )

    st.plotly_chart(grafico_classificacao, use_container_width=True)




# --- Times classificados e rebaixados ---
st.subheader(f"🏆 Libertadores e ❌ Rebaixados {ano_selecionado}")

if not df_filtrado_classificacao.empty:
    classificacao_ord = df_filtrado_classificacao.sort_values(by="Pontos", ascending=False)

    top4 = classificacao_ord.head(4)
    bottom4 = classificacao_ord.tail(4)

    # Juntar os dois para plotar
    destaques = pd.concat([top4, bottom4])

    # Criar coluna indicando situação
    destaques["Situacao"] = ["Libertadores" if i in top4.index else "Rebaixados" for i in destaques.index]

    largura_destaques = max(200, 50 * len(destaques))  # 

    grafico_destaques = px.bar(
        destaques,
        x="Time",
        y="Pontos",
        text="Pontos",
        color="Situacao",
        labels={"Pontos": "Total de Pontos", "Time": "Times", "Situacao": "Situação"},
        template="plotly_dark",
        width=largura_destaques
    )

    grafico_destaques.update_traces(textposition="outside")
    st.plotly_chart(grafico_destaques, use_container_width=True)

# --- Tabela de Dados Detalhados ---
st.subheader("📋 Dados Detalhados")
st.dataframe(
    df_filtrado_classificacao[['Temporada', 'Time', 'Pontos', 'Vitorias', 'Empates','Derrotas', 'Saldo_Gols']],
    use_container_width=True,
    hide_index=True
)

# --- Confrontos da Temporada ---
st.subheader("⚔️ Confrontos da Temporada")

# 1. Filtrar confrontos pela temporada selecionada
df_confrontos = df_final[df_final["Temporada"] == ano_selecionado].copy()

# 2. Aplicar o filtro de rodada se o usuário selecionou uma
if rodada_selecionada != "Todas":
    df_confrontos = df_confrontos[df_confrontos["Rodada"] == rodada_selecionada]

# 3. Aplicar o filtro de time para mostrar apenas jogos de times selecionados
df_confrontos = df_confrontos[
    (df_confrontos["Time_Casa"].isin(times_selecionados)) | 
    (df_confrontos["Time_Visitante"].isin(times_selecionados))
]

if not df_confrontos.empty:
    # Renomear as colunas para melhor visualização
    df_confrontos = df_confrontos.rename(columns={
        'Time_Casa': 'Mandante',
        'Time_Visitante': 'Visitante',
        'Gols_Mandante': 'Gols Mandante',
        'Gols_Visitante': 'Gols Visitante'
    })

    # Mostrar tabela dos confrontos filtrados
    st.dataframe(
        df_confrontos[['Rodada', 'Mandante', 'Gols Mandante', 'Visitante', 'Gols Visitante']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info(f"Sem confrontos disponíveis com os filtros selecionados.")