import pandas as pd
import torch
from transformers import pipeline
def sentiment_analysis(df):
    classifier = pipeline("text-classification", model = "j-hartmann/sentiment-roberta-large-english-3-classes", return_all_scores = True)
    texts = df["text"].tolist()
    sentiment_results = classifier(texts)
    df["sentiment"] = [r["label"] for r in sentiment_results]
    return df


def emotion_analysis(df):
    emotion_classifier = pipeline("text-classification", model = "j-hartmann/emotion-english-distilroberta-base")
    important_texts = df["text"].tolist()
    emotion_results = emotion_classifier(important_texts)
    df["emotion"] = [r["label"] for r in emotion_results]
    return df