import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import unicodedata
from collections import Counter

# ----------------------------
# CONFIGURAÇÃO DO APP
# ----------------------------
st.set_page_config(page_title="Fashion Law Analyzer", page_icon="👗", layout="centered")

st.title("👗 Fashion Law Analyzer")
st.subheader("Análise de Propriedade Intelectual e Contrafação na Moda")

# Palavras-chave principais
PALAVRAS_CHAVE = [
    'marca', 'registro', 'trademark', 'pirataria', 'contrafação',
    'imitação', 'trade dress', 'design', 'autoral',
    'propriedade intelectual', 'uso indevido', 'direitos autorais'
]

# ----------------------------
# FUNÇÕES AUXILIARES
# ----------------------------
def normalize_text(text):
    """Remove acentos, coloca minúsculas e normaliza espaços."""
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    return re.sub(r'\s+', ' ', text).strip()

def tokenize(text):
    """Retorna as palavras (tokens) de um texto."""
    return re.findall(r'\w+', text)

def analisar_textos(df, palavras_chave):
    """Conta ocorrências de palavras e frases em cada documento."""
    textos_norm = df['Texto_Documento'].fillna('').apply(normalize_text)

    contagem_palavras = Counter()
    contagem_por_doc = {}

    frases = [p for p in palavras_chave if ' ' in p]
    simples = [p for p in palavras_chave if ' ' not in p]

    simples_norm = [normalize_text(p) for p in simples]
    frases_norm = [normalize_text(p) for p in frases]

    for idx, texto in textos_norm.items():
        total_termos_doc = 0

        for frase in frases_norm:
            num = texto.count(frase)
            if num > 0:
                contagem_palavras[frase] += num
                total_termos_doc += num

        tokens = tokenize(texto)
        token_counts = Counter(tokens)
        for palavra in simples_norm:
            num = token_counts.get(palavra, 0)
            if num > 0:
                contagem_palavras[palavra] += num
                total_termos_doc += num

        contagem_por_doc[df.loc[idx, 'ID']] = total_termos_doc

    return contagem_palavras, contagem_por_doc

# ----------------------------
# INTERFACE STREAMLIT
# ----------------------------
st.markdown("Envie um arquivo CSV contendo uma coluna **Texto_Documento** para análise.")

uploaded_file = st.file_uploader("📁 Escolha o arquivo CSV", type=["csv"])

# Carrega CSV de exemplo se o usuário não enviar um
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Usando base de exemplo, pois nenhum arquivo foi enviado.")
    df = pd.DataFrame({
        'ID': [101, 102, 103, 104, 105],
        'Data': ['2025-01-10', '2025-02-15', '2025-03-20', '2025-04-01', '2025-05-05'],
        'Texto_Documento': [
            "A grande marca de luxo ingressou com ação de contrafação pelo design não autorizado do produto. A propriedade intelectual foi violada.",
            "Novo registro de marca para a coleção sustentável. A empresa protegeu sua marca e seu trade dress.",
            "Discussão sobre a proteção de direitos autorais em estampas de moda. A imitação de tecidos é uma preocupação.",
            "A pirataria de tênis continua sendo um desafio. Uso indevido de logo é recorrente.",
            "Registro da nova cor como marca tridimensional. Fortalecimento da proteção da marca."
        ]
    })

if st.button("🔍 Analisar"):
    if 'Texto_Documento' not in df.columns:
        st.error("O arquivo deve conter uma coluna chamada 'Texto_Documento'.")
    else:
        contagem_palavras, contagem_por_doc = analisar_textos(df, PALAVRAS_CHAVE)

        # Relatório textual
        st.subheader("📝 Relatório de Análise")
        st.write(f"**Total de documentos analisados:** {len(df)}")

        freq_df = pd.DataFrame(contagem_palavras.most_common(), columns=["Termo", "Frequência"])
        st.dataframe(freq_df)

        top_docs = sorted(contagem_por_doc.items(), key=lambda x: x[1], reverse=True)[:5]
        st.write("**Documentos com mais termos relevantes:**")
        st.table(pd.DataFrame(top_docs, columns=["ID do Documento", "Total de Ocorrências"]))

        # Gráfico de barras
        st.subheader("📊 Gráfico de Frequência de Termos")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(freq_df["Termo"].head(10), freq_df["Frequência"].head(10))
        ax.set_xlabel("Termos de Fashion Law")
        ax.set_ylabel("Frequência de Ocorrência")
        ax.set_title("Top 10 Termos de PI e Contrafação")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
