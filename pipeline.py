import pandas as pd
from ingestion import ingest_path
from Preprocessing import preprocessing
from sentiment_emotion_analysis import sentiment_analysis
from sentiment_emotion_analysis import emotion_analysis
from embeddings import embeddings
from Clustering import cluster
from cluster_analysis import cluster_analysis
def run_pipeline(input_path):
    df = ingest_path(input_path)
    df = preprocessing(df)
    df = sentiment_analysis(df)
    df = emotion_analysis(df)
    embedding_vectors = embeddings(df)
    df = cluster(embedding_vectors,df)

    #For the recommendations
    cluster_ids = df["cluster_id"].unique()
    insights = []
    for cid in cluster_ids:
        insight = cluster_analysis(df, cid)
        insights.append(insight)
    df_insights = pd.DataFrame(insights)
    return df, df_insights