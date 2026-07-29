import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import re
import json
import streamlit as st

def get_comments(df, cluster_id):
    comments = df.loc[df["cluster_id"] == cluster_id, "text"].tolist()
    return comments.sample(n = min(15, len(comments)), random_state = 107).tolist()

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

    prompt = f"""
"You are a customer experience analyst preparing insights for retail business leaders. Your goal is to summarize customer concerns and recommend practical actions that improve the customer experience."

A clustering algorithm has already grouped together customer feedback about the same issue.

Cluster Information:
- Dominant Sentiment: {sentiment}
- Dominant Emotion: {emotion}

Representative Customer Comments:
"""

    for comment in comments:
        prompt += f"- {comment}\n"

    prompt += """

Based only on the information above, return a JSON object with the following structure:

{
    "issue": "",
    "summary": "",
    "recommendation": ""
}

Requirements:
- "issue" should be a concise business-friendly label (2-5 words).
- "summary" should explain the common customer concern in 1-2 sentences.
- "recommendation" should provide one actionable recommendation for a business stakeholder.
- Return only valid JSON.
"""

    return prompt

load_dotenv()
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

def call_llm(prompt):
    

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
    