from typing import List, Dict
import pandas as pd


def analyze_response_schema(data: List[Dict]) -> Dict[str, str]:
    # analyze graph response schema
    schema: Dict[str, str] = {}
    for res in data:
        for key in res.keys():
            if key not in schema:
                schema[key] = type(res[key]).__name__
            else:
                if type(res[key]).__name__ != schema[key]:
                    schema[key] = "mixed"
    for key, value in schema.items():
        print(f"{key}: {value}")
    return schema


def analyze_column_usage(df: pd.DataFrame) -> pd.DataFrame:
    summary = []
    for column in df.columns:
        unique_values_count = df[column].nunique()
        null_values_count = df[column].isnull().sum()
        most_frequent_count = (
            df[column].value_counts().max() if unique_values_count > 0 else 0
        )

        # Determine if less than 10% of the dataset is using the column
        if null_values_count / len(df) > 0.9:
            status = "Less Than 10% Usage"
        # Determine the status based on unique values and their distribution
        elif unique_values_count == 1:
            status = "No Significant Differences"
        elif unique_values_count == 0 and null_values_count == len(df):
            status = "All Empty"
        elif unique_values_count == 2 and most_frequent_count >= len(df) - 1:
            status = "Low Variance"
        else:
            status = "Varied Values"

        summary.append(
            {
                "Column": column,
                "Unique Values Count": unique_values_count,
                "Null Values Count": null_values_count,
                "Most Frequent Value Count": most_frequent_count,
                "Status": status,
            }
        )

    summary_df = pd.DataFrame(summary)
    return summary_df
