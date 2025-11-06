

import streamlit as st
import requests
import plotly.express as px
from collections import Counter
from typing import Optional, Dict
from urllib.parse import urlencode

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"

st.set_page_config(page_title="Proposições por Deputado", layout="wide")

st.title("Proposições por Deputado — Câmara dos Deputados")

st.markdown("""
Este app consulta a **API de Dados Abertos da Câmara dos Deputados** e exibe:
- As proposições apresentadas por um deputado;
- Um **gráfico de temas** das proposições;
- Um **gráfico de evolução anual** das proposições.
""")


st.sidebar.header("Configurações")
api_key = st.sidebar.text_input("API Key", value="", type="password")

def make_headers() -> Dict[str,str]:
    headers = {"Accept": "application/json"}
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"
    return headers


@st.cache_data(show_spinner=False)
def buscar_deputados(nome: Optional[str] = None, pagina: int = 1, itens_por_pagina: int = 100):
    params = {"pagina": pagina, "itens": itens_por_pagina}
    if nome:
        params["nome"] = nome
    url = f"{API_BASE}/deputados?{urlencode(params)}"
    r = requests.get(url, headers=make_headers(), timeout=10)
    r.raise_for_status()
    return r.json().get("dados", [])

@st.cache_data(show_spinner=False)
def buscar_deputado_por_id(id_deputado: int):
    url = f"{API_BASE}/deputados/{id_deputado}"
    r = requests.get(url, headers=make_headers(), timeout=10)
    r.raise_for_status()
    return r.json().get("dados", {})

@st.cache_data(show_spinner=False)
def buscar_proposicoes_por_deputado(id_deputado:int, pagina:int=1, itens_por_pagina:int=200):
    params = {"idAutor": id_deputado, "pagina": pagina, "itens": itens_por_pagina}
    url = f"{API_BASE}/proposicoes?{urlencode(params)}"
    r = requests.get(url, headers=make_headers(), timeout=10)
    r.raise_for_status()
    return r.json().get("dados", [])


st.header(" Selecione o deputado")

col1, col2 = st.columns([3,1])
with col1:
    nome_busca = st.text_input("Nome do deputado:")
    deputados = buscar_deputados(nome_busca) if nome_busca else buscar_deputados()
    nomes = [f"{d['nome']} — ID:{d['id']} ({d['siglaPartido']}/{d['uf']})" for d in deputados]
    escolha = st.selectbox("Escolha um deputado:", [""] + nomes)
    selected_id = None
    if escolha:
        try:
            selected_id = int(escolha.split("ID:")[1].split()[0])
        except:
            selected_id = None

with col2:
    id_manual = st.text_input("Ou ID direto:")
    if id_manual.strip().isdigit():
        selected_id = int(id_manual.strip())

if not selected_id:
    st.info("Digite um nome ou ID de deputado acima.")
    st.stop()


deputado = buscar_deputado_por_id(selected_id)
st.subheader(f"{deputado.get('nome')} ({deputado.get('siglaPartido')}/{deputado.get('uf')})")
st.write(f"**E-mail:** {deputado.get('email','-')} | **URL:** {deputado.get('uri')}")


st.header("2️⃣ Proposições apresentadas")
dados = buscar_proposicoes_por_deputado(selected_id, pagina=1, itens_por_pagina=200)

if not dados:
    st.warning("Nenhuma proposição encontrada para este deputado.")
    st.stop()


for p in dados[:10]:
    st.markdown(f"- **{p.get('siglaTipo','')} {p.get('numero','')}/{p.get('ano','')}** — {p.get('ementa','')}")


st.header("3️⃣ Gráfico por tema")

temas = []
for p in dados:
    if p.get("temas"):
        for t in p["temas"]:
            if "nome" in t:
                temas.append(t["nome"])

if temas:
    contagem = Counter(temas)
    df_temas = [{"Tema": k, "Quantidade": v} for k, v in contagem.items()]
    fig_temas = px.bar(df_temas, x="Quantidade", y="Tema", orientation="h",
                       title="Distribuição de Proposições por Tema",
                       labels={"Tema": "Tema", "Quantidade": "Número de proposições"})
    st.plotly_chart(fig_temas, use_container_width=True)
else:
    st.info("A API não retornou temas detalhados para essas proposições.")


st.header("Gráfico de proposições por ano")

anos = [p.get("ano") for p in dados if p.get("ano")]
if anos:
    contagem_anos = Counter(anos)
    df_anos = [{"Ano": k, "Proposições": v} for k, v in sorted(contagem_anos.items())]
    fig_anos = px.line(df_anos, x="Ano", y="Proposições", markers=True,
                       title="Evolução do número de proposições por ano",
                       labels={"Ano": "Ano", "Proposições": "Número de proposições"})
    st.plotly_chart(fig_anos, use_container_width=True)
else:
    st.info("Não há dados de ano disponíveis para as proposições desse deputado.")
