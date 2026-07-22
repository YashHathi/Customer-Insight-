import pandas as pd
import numpy as np
from sklearn.cluster import HDBSCAN

def cluster(embeddings, df):
    cluster_model = HDBSCAN(min_cluster_size = 20, metric = 'cosine')
    clusters = cluster_model.fit_predict(embeddings)
    df["cluster_id"] = clusters
    df = df[df["cluster_id"] != -1]
    return df