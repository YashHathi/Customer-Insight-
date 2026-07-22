import pandas as pd
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def embeddings(df):
    embeddings = model.encode(df["text"].tolist())
    embeddings = pd.DataFrame(embeddings)
    return embeddings

