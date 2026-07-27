import json
import pandas as pd
from pathlib import Path
import argparse

# This function will help us gather files 
def get_input_files(input_path):
    path = Path(input_path)
    if path.is_dir():
        return sorted(
            [p for p in path.iterdir() if p.suffix.lower() in {".csv", ".xlsx", ".json"}]
        )
    if path.is_file():
        return [path]
    raise FileNotFoundError(f"Input not found: {input_path}")

# This function will help load the files
def load_file(file):
    suffix = file.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(file)
    elif suffix == ".xlsx":
        df = pd.read_excel(file)

    elif suffix == ".json":
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValueError("JSON must contain an object or list of objects.")

    else:
        raise ValueError(
            "Unsupported file type. Upload CSV, Excel, or JSON."
        )

    return df


# This function will help find the text columns
def find_text_columns(df):
    """
    Find possible customer feedback columns
    """

    keywords = [
        "text",
        "comment",
        "review",
        "feedback",
        "response",
        "description",
        "message"
    ]

    possible = []

    for col in df.columns:

        col_lower = col.lower()

        for word in keywords:
            if word in col_lower:
                possible.append(col)

    return possible


# This is for standardization
def standardize_data(
    df,
    text_column,
    timestamp_column=None,
):
    """
    Convert any dataset into standard format
    """

    output = pd.DataFrame()

    # Required
    output["text"] = (
        df[text_column]
        .astype(str)
        .str.strip()
    )


    # Optional timestamp
    if timestamp_column:
        output["timestamp"] = pd.to_datetime(
            df[timestamp_column],
            errors="coerce"
        )

    else:
        output["timestamp"] = None




    # Metadata
    output["source"] = "uploaded_file"


    # Remove empty feedback
    output = output[
        output["text"].notna()
        &
        (output["text"] != "")
    ]


    # Remove duplicates
    output = output.drop_duplicates(
        subset=["text"]
    )


    return output




# This function will help us ingest files from given path
def ingest_path(input_path):
    outputs = []

    for file_path in get_input_files(input_path):
        df = load_file(file_path)
        text_columns = find_text_columns(df)
        if not text_columns:
            print(f"Skipping {file_path.name}: no text column found.")
            continue

        text_column = text_columns[0]

        timestamp_column = next(
            (
                c
                for c in df.columns
                if c.lower() in {"timestamp", "date", "created_at", "review_date", "date_string"}
            ),
            None,
        )
        rating_column = next(
            (
                c
                for c in df.columns
                if c.lower() in {"rating", "score", "stars"}
            ),
            None,
        )

        output = standardize_data(
            df,
            text_column=text_column,
            timestamp_column=timestamp_column,
        )
        output["source"] = file_path.name
        outputs.append(output)

    if not outputs:
        return pd.DataFrame(columns=["text", "timestamp", "source"])
    return pd.concat(outputs, ignore_index=True)

# Entry point for the script
def main():
    parser = argparse.ArgumentParser(description="Ingest one or more files.")
    parser.add_argument("--input", required=True, help="Input file or directory")
    parser.add_argument("--output", required=True, help="Output CSV file")
    args = parser.parse_args()

    df = ingest_path(args.input)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()