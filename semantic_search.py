from openai import OpenAI
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# reading csv articles
df = pd.read_csv("NASA-Space-Challenges/SB_publications-main/SB_publication_PMC.csv")

model = SentenceTransformer('all-mpnet-base-v2')        # all-MiniLM-L6-v2
print ("tout fonctionne")
df['embedding'] = df['content'].apply(lambda x: model.encode(x))

query = "effets de la microgravité sur les plantes"
query_vec = model.encode(query)

df['similarity'] = df['embedding'].apply(lambda x: cosine_similarity([query_vec], [x])[0][0])
results = df.sort_values(by='similarity', ascending=False)
print(results[['title', 'similarity']])

print(df.head())

