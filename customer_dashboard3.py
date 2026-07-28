import streamlit as st
import pandas as pd
import matplotlib as plt
import plotly.express as px
from pipeline import run_pipeline

# Title
st.title("Customer Insight Engine")
st.write("Time:", pd.to_datetime("today"))

# File Uploader Button
uploaded_file = st.file_uploader("Upload Customer Insight Data", accept_multiple_files = True)

# This will give a file path for streamlit to read, as we are not hard coding for a specific file
import tempfile
if uploaded_file:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=uploaded_file.name
    ) as temp:

        temp.write(uploaded_file.getvalue())

        file_path = temp.name

# We will make a run analysis button which can allow for proper personalization
if st.button("Run Analysis"):
    with st.spinner("Running analysis..."):
        df, insights_df = run_pipeline(file_path)
        st.session_state["df"] = df
        st.session_state["insights_df"] = insights_df

if "df" not in st.session_state:
    st.stop()

df = st.session_state["df"]
insights_df = st.session_state["insights_df"]

st.divider()

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

active_clusters = base_df["label"].unique()
base_insights_df = insights_df[
    insights_df["label"].isin(active_clusters)
]

issue = st.sidebar.selectbox(
    "Select Issue", 
    ["All"] + sorted(base_insights_df["label"].unique())
)

# Filtering Data Frame
filtered_df = base_df.copy()
if issue != "All":
    cluster_id = base_insights_df[base_insights_df["label"] == issue].iloc[0]
    filtered_df = filtered_df[
        filtered_df["cluster_id"] == cluster_id]

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

if issue == "All":
    recommendation = "Select issue to see recommendation"
else: 
    recommendation = insights_df.loc[insights_df["label"] == issue, "recommendation"].iloc[0]
st.success(recommendation)

st.divider()

# Charts

# Feedback Distribution channels
feedback_counts = df.groupby(["label", "channel"]).size().reset_index(name = "Count")
chart1 = px.bar(feedback_counts, x = "label", y = "Count", color = "channel", barmode="stack", title = "Feedback Distribution by Issue and Channel")
st.plotly_chart(chart1)


sentiment_counts = df.groupby(["label", "sentiment"]).size().reset_index(name = "Count")
chart2 = px.bar(sentiment_counts, x = "label", y = "Count", color = "sentiment", barmode="stack", title = "Sentiment Distribution by Issue")
st.plotly_chart(chart2)

# Priority Matrix

priority = df.groupby("label").agg(volume = ("label", "size"), negativity = ("sentiment", lambda x: (x == "negative").mean())).reset_index()
chart3 = px.scatter(priority, x = "volume", y = "negativity", size = "volume", text = "label", title = "Priority Matrix: Volume vs Negativity")
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

