import streamlit as st
import requests
import plotly.express as px
from collections import Counter
from urllib.parse import urlencode
from typing import Optional, Dict

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
st.set_page_config(page_title="Painel Jurídico — Câmara dos Deputados", layout="wide")

st.title("Painel de Proposições — Câmara dos Deputados")

st.markdown("""
Este app consulta a **API de Dados Abertos da Câmara dos Deputados** e exibe:
- Proposições apresentadas por cada deputado;
- Um gráfico de **temas mais frequentes**;
- Um gráfico de **evolução anual das proposições**;
- Informações completas do parlamentar selecionado.
""")

def make_headers() -> Dict[str, str]:
    return {"Accept": "application/json"}

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
def buscar_proposicoes_por_deputado(id_deputado: int, pagina: int = 1, itens_por_pagina: int = 200):
    params = {"idAutor": id_deputado, "pagina": pagina, "itens": itens_por_pagina}
    url = f"{API_BASE}/proposicoes?{urlencode(params)}"
    r = requests.get(url, headers=make_headers(), timeout=10)
    r.raise_for_status()
    return r.json().get("dados", [])

st.sidebar.header("Pesquisa")
nome_busca = st.sidebar.text_input("Nome do deputado:")
deputados = buscar_deputados(nome_busca) if nome_busca else buscar_deputados()
nomes = [
    f"{d.get('nome', 'Desconhecido')} ({d.get('siglaPartido', '-')}/{d.get('uf', '-')}) — ID:{d.get('id', '-')}"
    for d in deputados
]
escolha = st.sidebar.selectbox("Escolha um deputado:", [""] + nomes)
selected_id = None

if escolha:
    try:
        selected_id = int(escolha.split("ID:")[1])
    except:
        selected_id = None

if not selected_id:
    st.info("Use o menu lateral para buscar e selecionar um deputado.")
    st.stop()

deputado = buscar_deputado_por_id(selected_id)

st.subheader(f"👤 {deputado.get('nome', 'Nome não disponível')}")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Partido:** {deputado.get('siglaPartido', '-')} / {deputado.get('uf', '-')}")
    st.write(f"**Situação:** {deputado.get('situacao', '-')}")
with col2:
    st.write(f"**E-mail:** {deputado.get('email', '-')}")
    gabinete = deputado.get('gabinete', {})
    st.write(f"**Gabinete:** {gabinete.get('predio', '-')}, sala {gabinete.get('sala', '-')}")
    st.write(f"**Andar:** {gabinete.get('andar', '-')}")

aba1, aba2, aba3 = st.tabs(["Proposições", "Temas", "Evolução Anual"])

with aba1:
    st.markdown("### Proposições apresentadas")
    dados = buscar_proposicoes_por_deputado(selected_id)
    if not dados:
        st.warning("Nenhuma proposição encontrada para este deputado.")
    else:
        for p in dados[:15]:
            st.markdown(f"- **{p.get('siglaTipo', '')} {p.get('numero', '')}/{p.get('ano', '')}** — {p.get('ementa', '')}")

with aba2:
    st.markdown("### Gráfico por tema")
    temas = []
    for p in dados:
        for t in p.get("temas", []):
            if "nome" in t:
                temas.append(t["nome"])
    if temas:
        contagem = Counter(temas)
        df_temas = [{"Tema": k, "Quantidade": v} for k, v in contagem.items()]
        fig_temas = px.bar(
            df_temas, x="Quantidade", y="Tema", orientation="h",
            title="Distribuição de Proposições por Tema",
            labels={"Tema": "Tema", "Quantidade": "Número de proposições"}
        )
        st.plotly_chart(fig_temas, use_container_width=True)
    else:
        st.info("A API não retornou temas detalhados para essas proposições.")

with aba3:
    st.markdown("### Evolução anual de proposições")
    anos = [p.get("ano") for p in dados if p.get("ano")]
    if anos:
        contagem_anos = Counter(anos)
        df_anos = [{"Ano": k, "Proposições": v} for k, v in sorted(contagem_anos.items())]
        fig_anos = px.line(
            df_anos, x="Ano", y="Proposições", markers=True,
            title="Evolução do número de proposições por ano",
            labels={"Ano": "Ano", "Proposições": "Número de proposições"}
        )
        st.plotly_chart(fig_anos, use_container_width=True)
    else:
        st.info("Não há dados de ano disponíveis para as proposições desse deputado.")
