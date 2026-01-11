import pandas as pd
import streamlit as st
import plotly.express as px



# Carregamento de dados:
@st.cache_data
def load_data():
    return pd.read_csv('focos_br_todos-sats_2024.csv')

df = load_data()

# Transformações iniciais do dataframe

df['data_pas'] = pd.to_datetime(df['data_pas'], errors='coerce')
df['mes'] = df['data_pas'].dt.month
df['dia_semana'] = df['data_pas'].dt.weekday

columns_to_check = df.columns.drop('frp')
df_cleaned = df.dropna(subset=columns_to_check)
df = df_cleaned.copy()

df = df[df['numero_dias_sem_chuva'] != -999]
df = df[df['risco_fogo'] != -999]




## ======== Dashboard em si ==========



# Introducao
st.set_page_config(page_title="Dashboard de Calor no Brasil", layout="wide")

st.title("Dashboard Interativo de Focos de Calor no Brasil")

st.markdown("""
Este dashboard permite a exploração interativa dos focos de calor registrados no Brasil em 2024.
Os dados são tratados dinamicamente e incluem informações temporais, geográficas e ambientais,
como estado, município, bioma e coordenadas geográficas. Os dados foram extraídos da base de dados do Instituto Nacional de Pesquisas Espaciais (INPE).
""")



# Botando sidebar
st.sidebar.header("Filtro para distribuição geográfica")

estados = sorted(df["estado"].unique())
estados.insert(0, "Todos os Estados")

estado_selecionado = st.sidebar.selectbox(
    "Selecione um estado:",
    estados
)

if estado_selecionado == "Todos os Estados":
    df_filtrado = df
else:
    df_filtrado = df[df["estado"] == estado_selecionado]




tab1, tab2= st.tabs(["Dados interativo", "Dados estáticos"])

with tab1:

    # Metricas principais
    total_focos = len(df_filtrado)

    bioma_mais_afetado = (
        df_filtrado["bioma"]
        .value_counts()
        .idxmax()
    )

    col1, col2 = st.columns(2)

    col1.metric("Total de focos", f"{total_focos:,}".replace(",", "."))
    col2.metric("Bioma mais afetado", bioma_mais_afetado)



    # Mapa geográfico
    st.subheader("Distribuição geográfica dos focos de calor")

    df_mapa = df_filtrado.sample(
        min(100_000, len(df_filtrado)),
        random_state=42
    )

    fig_mapa = px.scatter_map(
        df_mapa,
        lat="latitude",
        lon="longitude",
        hover_name="municipio",
        hover_data=["bioma"],
        zoom=3,
        height=500
    )

    fig_mapa.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0,"t": 0,"l": 0,"b":0}
    )

    st.plotly_chart(fig_mapa)



    # Mapa sazional por mês
    st.subheader("Distribuição temporal dos focos por mês")

    focos_por_mes = (
        df_filtrado.groupby("mes")
        .size()
        .reset_index(name="total_focos")
        .sort_values("mes")
    )

    fig_tempo = px.line(
        focos_por_mes,
        x="mes",
        y="total_focos",
        markers=True,
        labels={
            "mes": "Mês",
            "total_focos": "Número de focos"
        }
    )

    st.plotly_chart(fig_tempo)


    #Tabela
    st.subheader("Amostra dos dados filtrados")

    colunas_tabela = ["data_pas", "municipio", "bioma", "estado"]

    st.dataframe(df_filtrado[colunas_tabela].head(20), hide_index=True)


with tab2:
    st.subheader("Distribuição dos focos de queimadas por bioma")
    focos_por_bioma = (
        df.groupby('bioma')
        .size()
        .reset_index(name='total_focos')
        .sort_values('total_focos', ascending=False)
    )
    fig_focos_por_bioma = px.bar(
        focos_por_bioma,
        x='bioma',
        y='total_focos',
        labels={
            'bioma': 'Bioma',
            'total_focos': 'Número de focos'
        }
    )
    st.plotly_chart(fig_focos_por_bioma)
    
    

    st.subheader("Top 10 estados com maior número de focos de queimadas")
    focos_por_estado = (df.groupby('estado').size().
                    reset_index(name='total_focos').sort_values('total_focos', ascending=False))
    top_10_estados = focos_por_estado.head(10)
    fig_focos_por_estado = px.bar(
        top_10_estados,
        x='estado',
        y='total_focos',
        labels={
            'estado': 'Estado',
            'total_focos': 'Número de focos'
        }
    )
    st.plotly_chart(fig_focos_por_estado)
    top10_col1, top10_col2 = st.columns(2)
    
    with top10_col1:
        st.subheader("Contagem de focos dos top 10 estados com mais focos de calor")
        st.dataframe( top_10_estados.head(10),hide_index=True)
        
    with top10_col2:
        st.subheader("Top 10 munícipios com maior frequência de focos de calor")
        municipios = (df.groupby('municipio').size().
                        reset_index(name='total_focos').sort_values('total_focos', ascending=False))
        st.dataframe( municipios.head(10), hide_index=True)