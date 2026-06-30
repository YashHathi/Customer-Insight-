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

issue = st.sidebar.selectbox(
    "Select Issue", 
    ["All"] + sorted(base_df["label"].unique())
)

# Filtering Data Frame
filtered_df = base_df.copy()
if issue != "All":
    filtered_df = filtered_df[
        filtered_df["label"] == issue]

# For the date slider
latest_date = filtered_df["date"].max()
current = filtered_df[
    filtered_df["date"] >= latest_date - pd.Timedelta(days=6)
]

previous = filtered_df[
    (filtered_df["date"] >= latest_date - pd.Timedelta(days=13)) &
    (filtered_df["date"] < latest_date - pd.Timedelta(days=6))
]

# Compute Complaint Growth
current_count = len(current)
previous_count = len(previous)
growth = (current_count - previous_count) / max(previous_count,1)

# Convert Emotion into Scores
emotion_score = {
    "joy":0.1,
    "neutral":0.5,
    "surprise":0.3,
    "sadness":0.7,
    "fear":0.9,
    "anger":1.0,
    "frustration":1.0
}
emotion = filtered_df["emotion"].mode()[0]
emotion_value = emotion_score.get(
    emotion.lower(),
    0.5
)

# Get risk score
negative_rate = len(filtered_df[filtered_df["sentiment"] == "negative"]) / len(filtered_df)
trend_score = min(max(growth, 0), 1)
risk = (0.4 * trend_score) + (0.4 * negative_rate) + (0.2 * emotion_value)
if risk >= 0.75:
    status = "🔴 Critical"

elif risk >= 0.50:
    status = "🟡 Monitor"

else:
    status = "🟢 Stable"


left, right = st.columns(2)
left.metric(
    "Comments",
    len(filtered_df)
)

left.metric(
    "% Negativity",
    round(negative_rate * 100,2)
)

right.metric(
    "Primary Emotion",
    filtered_df["emotion"].mode()[0]
)

right.metric(
    "Emerging Risk",
    status
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

# Final Recommendation
st.subheader("Recommendation")
sentiment_level = filtered_df["sentiment"].mode()[0]

issue_rows = df[df["label"] == issue]

if issue_rows.empty:
    recommendation = "No recommendation available for this issue."
else:
    exact_match = issue_rows[issue_rows["sentiment"] == sentiment_level]
    if not exact_match.empty:
        recommendation = exact_match["recommendation_x"].iloc[0]
    else:
        recommendation = issue_rows["recommendation_x"].mode().iloc[0]
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

