import pandas as pd
from openai import OpenAI
import re
import json

def get_comments(df, cluster_id,n=5):
    filtered_df = df[df["cluster_id"] == cluster_id].head(n)
    comments = filtered_df["text"].tolist()
    return comments

def dominant_sentiment(df, cluster_id):
    filtered_df = df[df["cluster_id"] == cluster_id]
    sentiment_counts = filtered_df["sentiment"].value_counts()
    dominant_sentiment = sentiment_counts.idxmax()
    return dominant_sentiment

def dominant_emotion(df, cluster_id):
    filtered_df = df[df["cluster_id"] == cluster_id]
    emotion_counts = filtered_df["emotion"].value_counts()
    dominant_emotion = emotion_counts.idxmax()
    return dominant_emotion

def build_prompt(comments, sentiment, emotion):
    """
    Build an LLM prompt for analyzing a customer feedback cluster.
    """

    comment_text = "\n".join(
        f"- {comment}"
        for comment in comments
    )

    prompt = f"""
You are a customer experience analyst.

Analyze the following group of customer feedback.

Customer Comments:
{comment_text}

Overall Sentiment:
{sentiment}

Primary Emotion:
{emotion}

Your tasks are:

1. Give this customer issue a one word business-friendly name.
2. Write a 1-2 sentence summary describing the main customer concern.
3. Recommend one practical action the business should take.

Return only a valid JSON object in the following format:
{{
    "issue": "one word business-friendly name",
    "summary": "1-2 sentence summary",
    "recommendation": "one practical business action"
}}
"""

    return prompt

def call_llm(prompt):
    client = OpenAI(api_key="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")

    response = client.responses.create(
    model="gpt-5.4-nano",
    input=prompt,
    text={"format": {"type": "json_object"}}
    
    )
    output_text = response.output_text.strip()
    if output_text.startswith("```"):
        output_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_text).strip()
    return json.loads(output_text)


def cluster_analysis(df, cluster_id):
    comments = get_comments(df, cluster_id)
    sentiment = dominant_sentiment(df, cluster_id)
    emotion = dominant_emotion(df, cluster_id)
    prompt = build_prompt(comments, sentiment, emotion)
    result = call_llm(prompt)
    result["cluster_id"] = cluster_id
    return result
    