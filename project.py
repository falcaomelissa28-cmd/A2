pip install pandas matplotlib
python fashion_law_analyzer.py

import argparse
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import unicodedata
import sys
from pathlib import Path

PALAVRAS_CHAVE = [
    'marca', 'registro', 'trademark', 'pirataria', 'contrafacao',
    'contrafação', 'imitacao', 'imitação',
    'trade dress', 'design', 'autoral',
    'propriedade intelectual', 'uso indevido', 'direitos autorais'
]

def normalize_text(text):
    """Converte para minúsculas, remove acentos e normaliza espaços."""
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    """Retorna tokens alfanuméricos (palavras) de um texto normalizado."""
    return re.findall(r'\w+', text, flags=re.UNICODE)

def analisar_textos(dataframe, palavras_chave):
    """
    Conta ocorrências de palavras e frases em cada documento.
    Retorna: (Counter geral, dict contagem por documento)
    """
    if 'Texto_Documento' not in dataframe.columns:
        raise ValueError("O DataFrame não contém a coluna 'Texto_Documento'.")

     textos_norm = dataframe['Texto_Documento'].fillna('').apply(normalize_text)

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
              
doc_id = dataframe.loc[idx, 'ID'] if 'ID' in dataframe.columns else idx
        contagem_por_doc[doc_id] = total_termos_doc

    return contagem_palavras, contagem_por_doc

def gerar_relatorio_e_grafico(df, contagem_palavras, contagem_por_doc, top_n=10):
    print("\n--- RELATÓRIO DE ANÁLISE FASHION LAW ---")
    print(f"Total de Documentos Analisados: {len(df)}")
    print("-" * 40)
    print("Frequência Absoluta das Palavras/Frases (normalizadas):")
    for palavra, cont in contagem_palavras.most_common():
        print(f"- {palavra}: {cont}")
    print("-" * 40)

 ranking_sorted = sorted(contagem_por_doc.items(), key=lambda item: item[1], reverse=True)
    print("Top documentos com mais termos encontrados:")
    for doc_id, cont in ranking_sorted[:5]:
        print(f"ID {doc_id}: {cont} ocorrências")
    print("--- FIM DO RELATÓRIO ---\n")

 if contagem_palavras:
        top = dict(contagem_palavras.most_common(top_n))
        plt.figure(figsize=(10, 6))
        plt.bar(list(top.keys()), list(top.values()))
        plt.xlabel('Termos de Fashion Law (normalizados)')
        plt.ylabel('Frequência de Ocorrência')
        plt.title('Frequência dos Principais Termos de PI e Contrafação')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('frequencia_termos_fashion_law.png')
        print("Gráfico salvo em: frequencia_termos_fashion_law.png")
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Analisador de termos de PI e contrafação em textos de moda.")
    parser.add_argument('--input', '-i', default='dados_fashion_law.csv',
                        help='Caminho do CSV de entrada (padrão: dados_fashion_law.csv)')
    parser.add_argument('--top', '-t', type=int, default=10,
                        help='Número de termos a mostrar no gráfico')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Atenção: arquivo '{input_path}' não encontrado. Criando exemplo...")
        sample = {
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
df = pd.DataFrame(sample)
        df.to_csv(input_path, index=False)
        print(f"Arquivo exemplo criado em: {input_path}")
    else:
        df = pd.read_csv(input_path)

    contagem_palavras, contagem_por_doc = analisar_textos(df, PALAVRAS_CHAVE)
    gerar_relatorio_e_grafico(df, contagem_palavras, contagem_por_doc, top_n=args.top)

f __name__ == '__main__':
    main()

