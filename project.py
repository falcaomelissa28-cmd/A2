 import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re
import streamlit as st # Adicionar importação do Streamlit

# --- 1. CONFIGURAÇÃO E DADOS ---
st.title("⚖️ Análise de Frequência de Termos em Fashion Law")

PALAVRAS_CHAVE = [
    'marca', 'registro', 'trademark', 'pirataria', 'contrafação',
    'imitação', 'trade dress', 'design', 'autoral',
    'propriedade intelectual', 'uso indevido', 'direitos autorais'
]

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
# df.to_csv('dados_fashion_law.csv', index=False) # Removido para simplificar no Streamlit

# --- 2. FUNÇÃO DE ANÁLISE (Definição única e correta) ---
def analisar_textos(dataframe, palavras_chave):
    """Conta a ocorrência de palavras-chave nos textos."""
    textos_min = dataframe['Texto_Documento'].str.lower()

    contagem_palavras = Counter()
    contagem_por_doc = {}

    for index, texto in enumerate(textos_min):
        total_termos_doc = 0
        for palavra in palavras_chave:
            # Garante que apenas palavras inteiras sejam contadas (usando regex)
            ocorrencias = re.findall(r'\b' + re.escape(palavra) + r'\b', texto)
            num_ocorrencias = len(ocorrencias)
            
            if num_ocorrencias > 0:
                contagem_palavras[palavra] += num_ocorrencias
                total_termos_doc += num_ocorrencias
        
        contagem_por_doc[dataframe.loc[index, 'ID']] = total_termos_doc

    return contagem_palavras, contagem_por_doc

# --- 3. EXECUÇÃO DA ANÁLISE ---
frequencia_palavras, ranking_documentos = analisar_textos(df, PALAVRAS_CHAVE)


# --- 4. EXIBIÇÃO DOS RESULTADOS NO STREAMLIT ---
st.header("Relatório de Análise")

# Exibe a tabela de dados
st.subheader("Dados Originais Analisados")
st.dataframe(df)

# Exibe a frequência das palavras-chave
st.subheader("Frequência Absoluta das Palavras-Chave")
frequencia_df = pd.DataFrame(frequencia_palavras.most_common(), columns=['Termo', 'Frequência'])
st.table(frequencia_df)

# Exibe o ranking de documentos
st.subheader("Ranking de Documentos (IDs)")
ranking_sorted = sorted(ranking_documentos.items(), key=lambda item: item[1], reverse=True)
for id_doc, contagem in ranking_sorted:
    st.write(f"**ID {id_doc}**: {contagem} ocorrências totais.")

# --- 5. VISUALIZAÇÃO DO GRÁFICO (Corrigido para Streamlit) ---
if frequencia_palavras:
    st.subheader("Visualização Gráfica")
    top_palavras = dict(frequencia_palavras.most_common(10))
    
    # Cria a figura do Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(top_palavras.keys(), top_palavras.values(), color='skyblue')
    plt.xlabel('Termos de Fashion Law')
    plt.ylabel('Frequência de Ocorrência')
    plt.title('Frequência dos Principais Termos de PI e Contrafação')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # st.pyplot() é a função correta para exibir o gráfico
    st.pyplot(plt)
