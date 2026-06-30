import streamlit as st
import pandas as pd
import matplotlib as plt
import plotly.express as px

# Data
df = pd.read_csv("Customer_insight.csv")

# Title
st.title("Customer Insight Engine")
st.write("Time:", pd.to_datetime("today"))

# KPI Cards
# col1,col2,col3,col4 = st.columns(4)
# col1.metric(
#     "# Feedback", 
#      len(df))

# col2.metric(
#     "% Negativity",
#     round((len(df[df.sentiment == "negative"]) / len(df)) * 100,2)
# )

# col3.metric(
#     "Feedback Intents",
#     df["label"].nunique()
# )

# col4.metric(
#     "Emotions",
#     df["emotion"].nunique()
# )

# st.divider()

# Filter Button 

df["date"] = pd.to_datetime(df["timestamp"])

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.sidebar.slider(
    "Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)



base_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
]

intent = st.sidebar.selectbox(
    "Select Intent", 
    ["All"] + sorted(base_df["label"].unique())
)


# Filtering Data Frame
filtered_df = base_df.copy()

if intent != "All":
    filtered_df = filtered_df[
        filtered_df["label"] == intent]



left, right = st.columns(2)
left.metric(
    "Comments",
    len(filtered_df)
)

left.metric(
    "% Negativity",
    round((len(filtered_df[filtered_df.sentiment == "negative"]) / len(filtered_df)) * 100,2)
)

right.metric(
    "Primary Emotion",
    filtered_df["emotion"].mode()[0]
)

right.metric(
    "Priority",
    "🔴 High"
    if (filtered_df["sentiment"]=="negative").mean() > .80
    else "🟡 Medium"
)

st.divider()

#Issue Explorer
st.subheader("Sample Comments")
samples = filtered_df.sample(min(5, len(filtered_df)), random_state=107)
for _, row in samples.iterrows():

    with st.container(border=True):

        st.markdown(f"**Customer Comment**")

        st.write(row["raw_text"])

        col1, col2 = st.columns(2)

        col1.metric("Sentiment", row["sentiment"].title())
        col2.metric("Emotion", row["emotion"].title())

st.subheader("Recommendation")
recommendation = filtered_df["recommendation"].iloc[0]
st.success(recommendation)

st.divider()

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

sentiment_filter = st.selectbox(
    "Trend Sentiment",
    ["All"] + sorted(df["sentiment"].unique())
)

trend_df = filtered_df.copy()

if sentiment_filter != "All":
    trend_df = trend_df[
        trend_df["sentiment"] == sentiment_filter
    ]

trend = (
    trend_df
    .groupby(
        [
            filtered_df["date"].dt.date,
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
    title="Customer Issue Trends Over Time"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

