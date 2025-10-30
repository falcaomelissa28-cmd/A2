pandas 
matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re

# --- 1. CONFIGURAÇÃO E DADOS SIMULADOS ---

PALAVRAS_CHAVE = [
    'marca', 'registro', 'trademark', 'pirataria', 'contrafação',
    'imitação', 'trade dress', 'design', 'autoral', 'propriedade intelectual',
    'uso indevido', 'direitos autorais'
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
df.to_csv('dados_fashion_law.csv', index=False)

# --- 2. FUNÇÃO DE ANÁLISE ---

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

# --- 3. EXECUÇÃO DA ANÁLISE ---

frequencia_palavras, ranking_documentos = analisar_textos(df, PALAVRAS_CHAVE)

# --- 4. RELATÓRIO ---

print("\n--- 📝 RELATÓRIO DE ANÁLISE FASHION LAW ---")
print(f"Total de Documentos Analisados: {len(df)}")
print("-" * 40)
print("Frequência Absoluta das Palavras-Chave:")
for palavra, contagem in frequencia_palavras.most_common():
    print(f"- {palavra.capitalize()}: {contagem}")
print("-" * 40)
ranking_sorted = sorted(ranking_documentos.items(), key=lambda x: x[1], reverse=True)
print("Ranking dos Documentos com Mais Termos:")
for id_doc, contagem in ranking_sorted[:3]:
    print(f"ID {id_doc}: {contagem} ocorrências")
print("--- FIM DO RELATÓRIO ---\n")

# --- 5. GRÁFICO ---

if frequencia_palavras:
    top_palavras = dict(frequencia_palavras.most_common(10))
    plt.figure(figsize=(10, 6))
    plt.bar(top_palavras.keys(), top_palavras.values())
    plt.title('Frequência de Termos de PI e Contrafação na Moda')
    plt.xlabel('Termos')
    plt.ylabel('Frequência')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('frequencia_termos_fashion_law.png')
    plt.show()
