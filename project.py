import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlencode
from typing import Optional

st.set_page_config(page_title="Análise de Deputados", layout="wide")
st.title("Painel de Deputados Federais — Dados Abertos da Câmara")

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"

def make_headers():
    return {"User-Agent": "Mozilla/5.0 (Streamlit App)"}

def requisitar_json(url: str):
    """Faz uma requisição segura e retorna JSON ou None se falhar."""
    try:
        r = requests.get(url, headers=make_headers(), timeout=10)
        if r.status_code != 200:
            st.warning(f"Erro {r.status_code} ao acessar a API ({url}).")
            return None
        return r.json()
    except Exception as e:
        st.error(f"Falha na conexão com a API: {e}")
        return None

@st.cache_data(show_spinner=False)
def buscar_deputados(nome: Optional[str] = None, pagina: int = 1, itens_por_pagina: int = 100):
    params = {"pagina": pagina, "itens": itens_por_pagina}
    if nome:
        params["nome"] = nome
    url = f"{API_BASE}/deputados?{urlencode(params)}"
    dados = requisitar_json(url)
    return dados.get("dados", []) if dados else []

@st.cache_data(show_spinner=False)
def buscar_deputado_por_id(id_deputado: int):
    url = f"{API_BASE}/deputados/{id_deputado}"
    dados = requisitar_json(url)
    return dados.get("dados", {}) if dados else {}

@st.cache_data(show_spinner=False)
def buscar_proposicoes_por_deputado(id_deputado: int, pagina: int = 1, itens_por_pagina: int = 200):
    params = {"idAutor": id_deputado, "pagina": pagina, "itens": itens_por_pagina}
    url = f"{API_BASE}/proposicoes?{urlencode(params)}"
    dados = requisitar_json(url)
    return dados.get("dados", []) if dados else []

st.sidebar.header("Buscar Deputado")
nome_busca = st.sidebar.text_input("Digite o nome do deputado:")
botao_buscar = st.sidebar.button("Buscar")

deputados = []
if botao_buscar and nome_busca.strip():
    with st.spinner("Buscando deputados..."):
        deputados = buscar_deputados(nome_busca.strip())

if deputados:
    nomes = [f"{d['nome']} ({d.get('siglaPartido', '?')}/{d.get('siglaUf', '?')})" for d in deputados]
    selecionado = st.sidebar.selectbox("Selecione um deputado:", nomes)
    deputado = deputados[nomes.index(selecionado)]
    selected_id = deputado["id"]

    dados_dep = buscar_deputado_por_id(selected_id)
    proposicoes = buscar_proposicoes_por_deputado(selected_id)

    tab1, tab2 = st.tabs(["Informações Gerais", "Proposições"])

    with tab1:
        st.subheader(f"{dados_dep.get('nomeCivil', deputado['nome'])}")
        col1, col2 = st.columns([1, 3])
        with col1:
            if "urlFoto" in deputado:
                st.image(deputado["urlFoto"], width=150)
        with col2:
            st.write(f"**Partido:** {deputado.get('siglaPartido', 'N/A')} / {deputado.get('siglaUf', 'N/A')}")
            st.write(f"**Email:** {dados_dep.get('ultimoStatus', {}).get('gabinete', {}).get('email', 'Não disponível')}")
            st.write(f"**Situação:** {dados_dep.get('ultimoStatus', {}).get('situacao', 'Desconhecida')}")

        if dados_dep.get("redeSocial"):
            st.markdown("**Redes sociais:**")
            for link in dados_dep["redeSocial"]:
                st.markdown(f"- [{link}]({link})")

    with tab2:
        st.subheader("Proposições apresentadas")

        if proposicoes:
            df = pd.DataFrame(proposicoes)
            st.dataframe(df[["id", "siglaTipo", "numero", "ano", "ementa"]], use_container_width=True)

            # --- Gráfico: Quantidade de proposições por tipo ---
            graf = df["siglaTipo"].value_counts().reset_index()
            graf.columns = ["Tipo", "Quantidade"]

            fig, ax = plt.subplots()
            ax.bar(graf["Tipo"], graf["Quantidade"])
            ax.set_xlabel("Tipo de proposição")
            ax.set_ylabel("Quantidade")
            ax.set_title("Distribuição de proposições por tipo")
            st.pyplot(fig)

        else:
            st.info("Nenhuma proposição encontrada para este deputado.")
else:
    st.info("Digite um nome e clique em 'Buscar' para começar.")
