"""
Data Preparation and Feature Engineering Script
Reads historical bin data from Firebase, cleans it, computes features,
and prepares it for training.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import json
import os


# Initialize Firebase
def init_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://smart-waste-3d7d0-default-rtdb.europe-west1.firebasedatabase.app/"
            },
        )


def fetch_historical_data():
    """Fetch all historical data from Firebase /history"""
    print("Fetching historical data from Firebase...")
    ref = db.reference("/history")
    history_data = ref.get()

    if not history_data:
        raise ValueError("No historical data found in Firebase")

    # Convert nested Firebase data to list of records
    records = []
    for bin_id, timestamps in history_data.items():
        if timestamps:
            for timestamp, data in timestamps.items():
                record = {
                    "bin_id": bin_id,
                    "timestamp": int(timestamp),
                    "fill_level": data.get("fill_level", 0),
                    "latitude": data.get("latitude", 0),
                    "longitude": data.get("longitude", 0),
                }
                records.append(record)

    print(f"Fetched {len(records)} historical records")
    return pd.DataFrame(records)


def clean_data(df):
    """Clean and preprocess the raw data"""
    print("Cleaning data...")

    # Convert timestamp to datetime
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

    # Remove invalid fill levels
    df = df[(df["fill_level"] >= 0) & (df["fill_level"] <= 100)]

    # Remove rows with missing critical data
    df = df.dropna(subset=["bin_id", "timestamp", "fill_level"])

    # Sort by bin_id and timestamp
    df = df.sort_values(["bin_id", "timestamp"]).reset_index(drop=True)

    # Remove duplicate timestamps for same bin
    df = df.drop_duplicates(subset=["bin_id", "timestamp"], keep="last")

    print(f"After cleaning: {len(df)} records")
    return df


def compute_fill_rate(group):
    """Compute fill rate (percentage change per hour) for a bin's time series"""
    group = group.sort_values("timestamp").copy()

    # Calculate time differences in hours
    group["time_diff_hours"] = group["timestamp"].diff() / 3600

    # Calculate fill level differences
    group["fill_diff"] = group["fill_level"].diff()

    # Calculate fill rate (percentage per hour)
    group["fill_rate"] = np.where(
        group["time_diff_hours"] > 0, group["fill_diff"] / group["time_diff_hours"], 0
    )

    # Handle negative fill rates (bin was emptied) - set to 0
    group["fill_rate"] = group["fill_rate"].clip(lower=0)

    # First row has no previous data
    group.loc[group.index[0], "fill_rate"] = 0

    return group


def compute_rolling_features(group, window=3):
    """Compute rolling statistics for fill rate"""
    group = group.sort_values("timestamp").copy()

    # Rolling mean of fill rate
    group["fill_rate_rolling_mean"] = (
        group["fill_rate"].rolling(window=window, min_periods=1).mean()
    )

    # Rolling std of fill rate
    group["fill_rate_rolling_std"] = (
        group["fill_rate"].rolling(window=window, min_periods=1).std().fillna(0)
    )

    return group


def compute_time_features(df):
    """Extract time-based features"""
    df["hour"] = df["datetime"].dt.hour
    df["weekday"] = df["datetime"].dt.weekday
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)
    return df


def compute_time_to_full(group):
    """Compute time to full (hours) for each record."""
    group = group.sort_values("timestamp").copy()
    time_to_full = []

    for idx, row in group.iterrows():
        current_time = row["timestamp"]
        current_fill = row["fill_level"]

        if current_fill >= 100:
            time_to_full.append(0)
        else:
            # Look forward to find when it becomes full
            future_data = group[group["timestamp"] > current_time]
            full_records = future_data[future_data["fill_level"] >= 100]

            if len(full_records) > 0:
                time_to_full_seconds = full_records.iloc[0]["timestamp"] - current_time
                time_to_full_hours = time_to_full_seconds / 3600
                time_to_full.append(time_to_full_hours)
            else:
                # Estimate based on fill rate if no full record found
                if row["fill_rate"] > 0:
                    remaining_capacity = 100 - current_fill
                    estimated_hours = remaining_capacity / row["fill_rate"]
                    time_to_full.append(min(estimated_hours, 168))
                else:
                    time_to_full.append(168)

    group["time_to_full_hours"] = time_to_full
    return group


def engineer_features(df):
    """Complete feature engineering pipeline"""
    print("Engineering features...")

    # Compute fill rate per bin
    df = df.groupby("bin_id", group_keys=False).apply(compute_fill_rate)

    # Compute rolling statistics per bin
    df = df.groupby("bin_id", group_keys=False).apply(compute_rolling_features)

    # FIX: Handle NaN values created by rolling windows (first few rows)
    # Fill forward then backward to ensure no gaps
    df = df.groupby("bin_id", group_keys=False).apply(lambda x: x.ffill().bfill())
    df = df.fillna(0)  # Final safety net

    # Add time-based features
    df = compute_time_features(df)

    # Compute target variable (time to full)
    print("Computing time to full (this may take a moment)...")
    df = df.groupby("bin_id", group_keys=False).apply(compute_time_to_full)

    # Remove rows with invalid targets
    df = df[df["time_to_full_hours"] > 0]

    print(f"Feature engineering complete: {len(df)} records with features")
    return df


def save_prepared_data(df, output_path="data/prepared_data.csv"):
    """Save the prepared dataset"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Prepared data saved to {output_path}")

    print("\n=== Dataset Summary ===")
    print(f"Total records: {len(df)}")
    print(f"Unique bins: {df['bin_id'].nunique()}")
    print(f"Target statistics (time_to_full_hours):")
    print(df["time_to_full_hours"].describe())


def main():
    try:
        init_firebase()
        df = fetch_historical_data()
        df = clean_data(df)
        df = engineer_features(df)
        save_prepared_data(df)
        print("\n✓ Data preparation completed successfully!")
    except Exception as e:
        print(f"Error during data preparation: {e}")
        raise


if __name__ == "__main__":
    main()
