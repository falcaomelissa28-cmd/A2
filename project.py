import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlencode

st.set_page_config(page_title="Painel de Deputados", layout="wide")
st.title("Painel de Deputados Federais — Dados Abertos da Câmara")

API_BASE = "https://dadosabertos.camara.leg.br/api/v2"

def requisitar_json(url: str):
    """
    Faz requisição segura e retorna JSON.
    Retorna None em caso de erro de conexão ou HTTP.
    """
    try:
     
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
      
        print(f"Erro HTTP ao acessar {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/timeout: {e}")
        return None

@st.cache_data(show_spinner=False)
def buscar_deputados(nome):
    """Busca deputados por nome."""
    url = f"{API_BASE}/deputados?{urlencode({'nome': nome, 'itens': 100})}"
    dados = requisitar_json(url)
    return dados.get("dados", []) if dados else None 

@st.cache_data(show_spinner=False)
def buscar_deputado_por_id(id_deputado):
    """Retorna detalhes de um deputado."""
    url = f"{API_BASE}/deputados/{id_deputado}"
    dados = requisitar_json(url)
    return dados.get("dados", {}) if dados else None

@st.cache_data(show_spinner=False)
def buscar_proposicoes_por_deputado(id_deputado):
    """Busca proposições de um deputado."""
    params = {"idDeputadoAutor": id_deputado, "itens": 100}
    url = f"{API_BASE}/proposicoes?{urlencode(params)}"
    dados = requisitar_json(url)
    return dados.get("dados", []) if dados else None

st.sidebar.header("Buscar Deputado")
nome_busca = st.sidebar.text_input("Digite o nome do deputado:")
buscar_btn = st.sidebar.button("Buscar")

if buscar_btn and nome_busca.strip():
    with st.spinner("Buscando deputados..."):
        deputados = buscar_deputados(nome_busca.strip())

   
    if deputados is None:
        st.error(" **Ops! Parece que tivemos um problema de conexão com o servidor da Câmara.** Por favor, tente novamente mais tarde.")
    elif not deputados:
        st.warning(f" **Que pena!** Nenhum deputado encontrado com o nome **{nome_busca.strip()}**.")
   
    else:
        nomes = [f"{d['nome']} ({d.get('siglaPartido', '?')}/{d.get('siglaUf', '?')})" for d in deputados]
        selecionado = st.sidebar.selectbox("Selecione um deputado:", nomes)
        deputado = deputados[nomes.index(selecionado)]
        id_dep = deputado["id"]

        dados_dep = buscar_deputado_por_id(id_dep)
        proposicoes = buscar_proposicoes_por_deputado(id_dep)

        
        if dados_dep is None or proposicoes is None:
            st.error(" **Algo deu errado ao carregar os detalhes do deputado.** Tente recarregar a página ou selecionar outro deputado.")
        else:
            tab1, tab2 = st.tabs([" Informações Gerais", "Proposições"])

            with tab1:
                st.subheader(f"{dados_dep.get('nomeCivil', deputado['nome'])}")
                col1, col2 = st.columns([1, 3])
                with col1:
                    if "urlFoto" in deputado:
                        st.image(deputado["urlFoto"], width=150)
                with col2:
                    st.write(f"**Partido:** {deputado.get('siglaPartido', 'N/A')} / {deputado.get('siglaUf', 'N/A')}")
                    email = dados_dep.get("ultimoStatus", {}).get("gabinete", {}).get("email", "Não disponível")
                    st.write(f"**Email:** {email}")
                    situacao = dados_dep.get("ultimoStatus", {}).get("situacao", "Desconhecida")
                    st.write(f"**Situação:** {situacao}")

            with tab2:
                st.subheader("Proposições apresentadas")

                if not proposicoes:
                    st.info("Nenhuma proposição encontrada para este deputado.")
                else:
                    df = pd.DataFrame(proposicoes)
                    st.dataframe(df[["id", "siglaTipo", "numero", "ano", "ementa"]], use_container_width=True)

                    graf = df["siglaTipo"].value_counts().reset_index()
                    graf.columns = ["Tipo", "Quantidade"]

                    fig, ax = plt.subplots()
                    ax.bar(graf["Tipo"], graf["Quantidade"])
                    ax.set_xlabel("Tipo de proposição")
                    ax.set_ylabel("Quantidade")
                    ax.set_title("Distribuição de proposições por tipo")
                    st.pyplot(fig)
else:
    st.info("Digite o nome de um deputado e clique em **Buscar** para começar.")
