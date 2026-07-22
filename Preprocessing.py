import pandas
import re

# Remove missing values
def remove_missing_values(df):
    df = df.copy()
    df = df.dropna(subset=["text"])
    df = df[df["text"].str.strip() != ""]
    return df

# Removing Duplicate values
def remove_duplicate_values(df):
    return df.drop_duplicates(subset=["text"])

# Clean Text
def clean_text(text):
    text = str(text)
    text = text.strip()
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Final Preprocessing
def preprocessing(df):
    df = remove_missing_values(df)
    df = remove_duplicate_values(df)
    df["text"] = df["text"].apply(clean_text)
    return df
