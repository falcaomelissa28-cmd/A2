import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Propostas de Deputados", layout="wide")

st.title("Propostas Legislativas — Câmara dos Deputados")


@st.cache_data
def buscar_deputados():
    url = "https://dadosabertos.camara.leg.br/api/v2/deputados?itens=200"
    r = requests.get(url)
    r.raise_for_status()
    dados = r.json()
    return dados["dados"]


@st.cache_data
def buscar_proposicoes_por_deputado(deputado_id):
    url = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?itens=100&idDeputadoAutor={deputado_id}"
    r = requests.get(url)
    r.raise_for_status()
    dados = r.json()
    return dados["dados"]


st.sidebar.header("Escolha um deputado")
deputados = buscar_deputados()
nomes = [f"{d.get('nome', 'Desconhecido')} ({d.get('siglaPartido', '-')}/{d.get('uf', '-')})" for d in deputados]
nome_escolhido = st.sidebar.selectbox("Deputado:", nomes)


indice = nomes.index(nome_escolhido)
deputado = deputados[indice]
deputado_id = deputado["id"]


st.subheader(f"Informações sobre {deputado['nome']}")
col1, col2 = st.columns(2)
with col1:
    st.image(deputado["urlFoto"], width=200)
with col2:
    st.write(f"**Nome:** {deputado['nome']}")
    st.write(f"**Partido:** {deputado['siglaPartido']} / {deputado['uf']}")
    st.write(f"**ID:** {deputado['id']}")
    st.write(f"**E-mail:** {deputado.get('email', 'Não informado')}")


st.subheader("Proposições apresentadas")
proposicoes = buscar_proposicoes_por_deputado(deputado_id)

if not proposicoes:
    st.info("Nenhuma proposição encontrada para este deputado.")
else:
    df = pd.DataFrame(proposicoes)
    df["ano"] = pd.to_datetime(df["dataApresentacao"]).dt.year
    st.dataframe(df[["id", "siglaTipo", "numero", "ano", "ementa"]])

    
    st.subheader("Gráfico: Proposições por ano")
    grafico = df.groupby("ano").size().reset_index(name="Quantidade")
    fig = px.bar(grafico, x="ano", y="Quantidade", title="Proposições apresentadas por ano", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
