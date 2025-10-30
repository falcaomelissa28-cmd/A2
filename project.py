
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re

st.set_page_config(page_title="Fashion Law PI Monitor", page_icon="👗")

st.title("👗 Fashion Law PI Monitor")
st.write("Análise de Propriedade Intelectual e Contrafação na Moda")


PALAVRAS_CHAVE = [
    'marca', 'registro', 'trademark', 'pirataria', 'contrafação',
    'imitação', 'trade dress', 'design', 'autoral', 'propriedade intelectual',
    'uso indevido', 'direitos autorais'
]


uploaded_file = st.file_uploader("📂 Envie um arquivo CSV com os textos (opcional)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Usando base de dados simulada...")
    data = {
        'ID': [101, 102, 103, 104, 105],
        'Data': ['2025-01-10', '2025-02-15', '2025-03-20', '2025-04-01', '2025-05-05'],
        'Texto_Documento': [
            "A grande marca de luxo ingressou com ação de contrafação pelo design não autorizado do produto. A propriedade intelectual foi violada.",
            "Novo registro de marca para a coleção sustentável. A empresa protegeu sua marca e seu trade dress.",
            "Discussão sobre a proteção de direitos autorais em estampas de moda. A imitação de tecidos é uma preocupação.",
            "A pirataria de tênis continua sendo um desafio. Uso indevido de logo é recorrente.",
            "Registro da nova cor como marca tridimensional. Fortalecimento da proteção da marca."
        ]
    }
    df = pd.DataFrame(data)


def analisar_textos(dataframe, palavras_chave):
    textos_min = dataframe['Texto_Documento'].str.lower()
    contagem_palavras = Counter()
    contagem_por_doc = {}

    for index, texto in enumerate(textos_min):
        total_termos_doc = 0
        for palavra in palavras_chave:
            ocorrencias = re.findall(r'\b' + re.escape(palavra) + r'\b', texto)
            num_ocorrencias = len(ocorrencias)
            if num_ocorrencias > 0:
                contagem_palavras[palavra] += num_ocorrencias
                total_termos_doc += num_ocorrencias
        contagem_por_doc[dataframe.loc[index, 'ID']] = total_termos_doc

    return contagem_palavras, contagem_por_doc


if st.button("🔍 Analisar Textos"):
    freq, ranking = analisar_textos(df, PALAVRAS_CHAVE)

    st.subheader("📊 Frequência das Palavras-Chave")
    freq_df = pd.DataFrame(freq.items(), columns=["Palavra", "Frequência"]).sort_values("Frequência", ascending=False)
    st.dataframe(freq_df)

    st.subheader("🏆 Top 3 Documentos com mais termos de interesse")
    ranking_sorted = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    top_docs = pd.DataFrame(ranking_sorted[:3], columns=["ID do Documento", "Ocorrências"])
    st.table(top_docs)

    
    st.subheader("📈 Gráfico de Frequência")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(freq_df["Palavra"], freq_df["Frequência"], color="skyblue")
    plt.xticks(rotation=45, ha="right")
    plt.title("Frequência de Termos de PI e Contrafação")
    st.pyplot(fig)
