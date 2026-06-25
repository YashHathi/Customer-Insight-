import streamlit as st
import pandas as pd
import plotly.express as px

# Data
df = pd.read_csv("Customer_insight.csv")

# Title
st.title("Customer Insight Engine")
st.write("Time:", pd.to_datetime("today"))

# Filter Button 
intent = st.sidebar.selectbox(
    "Select Intent", 
    ["All"] + sorted(df["label"].unique())
)


sentiment = st.sidebar.selectbox(
    "Select Sentiment", 
    ["All"] + sorted(df["sentiment"].unique())
)




# Filtering Data Frame
filtered_df = df.copy()

if intent != "All":
    filtered_df = filtered_df[
        filtered_df["label"] == intent
    ]

if sentiment != "All":
    filtered_df = filtered_df[
        filtered_df["sentiment"] == sentiment
    ]

# KPI Cards
col1,col2,col3,col4 = st.columns(4)
col1.metric(
    "# Feedback", 
     len(df))

col2.metric(
    "% Negativity",
    round((len(df[df.sentiment == "negative"]) / len(df)) * 100,2)
)

col3.metric(
    "Feedback Intents",
    df["label"].nunique()
)

col4.metric(
    "Emotions",
    df["emotion"].nunique()
)


# Charts


sentiment_counts = df.groupby(["label", "sentiment"]).size().reset_index(name = "Count")
chart2 = px.bar(sentiment_counts, x = "label", y = "Count", color = "sentiment", barmode="stack")
st.plotly_chart(chart2)

# Priority Matrix

priority = df.groupby("label").agg(volume = ("label", "size"), negativity = ("sentiment", lambda x: (x == "negative").mean())).reset_index()
chart3 = px.scatter(priority, x = "volume", y = "negativity", size = "volume", text = "label")
chart3.update_traces(textposition = "top center")
st.plotly_chart(chart3)

st.divider()

# Trend Chart

filtered_df["date"] = pd.to_datetime(filtered_df["timestamp"])

min_date = filtered_df["date"].min().date()
max_date = filtered_df["date"].max().date()

start_date, end_date = st.sidebar.slider(
    "Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

base_df = filtered_df[
    (filtered_df["date"].dt.date >= start_date) &
    (filtered_df["date"].dt.date <= end_date)
]

trend = (
    base_df
    .groupby(
        [
            base_df["date"].dt.date,
            "label"
        ]
    )
    .size()
    .reset_index(name="Count")
)

fig = px.line(
    trend,
    x="date",
    y="Count",
    color="label",
    markers=True,
    title="Customer Issue Trends"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# Issue Explorer
st.subheader("Sample Comments")
if "raw_text" in filtered_df.columns:
    samples = filtered_df["raw_text"].sample(min(5, len(filtered_df)), random_state=107)
    for c in samples:
        st.write(".", c)

st.subheader("Recommendation")
recommendation = filtered_df["recommendation"].iloc[0]
st.info(recommendation)