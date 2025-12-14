"""
Inference Module
Fetches bin data, calculates fill rates based on history,
and predicts time-to-full.
"""

import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import time
import joblib
from datetime import datetime

# Configuration
HISTORY_LIMIT = 10  # Number of past data points to check for fill rate


def init_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://smart-waste-3d7d0-default-rtdb.europe-west1.firebasedatabase.app/"
            },
        )


def fetch_current_bin_states():
    """Fetch current state of all bins"""
    print("Fetching current bin states...")
    ref = db.reference("/bins")
    data = ref.get()

    if not data:
        return pd.DataFrame()

    records = []
    for bin_id, val in data.items():
        records.append(
            {
                "bin_id": bin_id,
                # FIX: Ensure fill_level is a float
                "fill_level": float(val.get("fill_level", 0)),
                "latitude": val.get("latitude", 0),
                "longitude": val.get("longitude", 0),
                # FIX: Ensure timestamp is a float
                "last_updated": float(val.get("timestamp", time.time())),
            }
        )

    df = pd.DataFrame(records)
    print(f"Fetched {len(df)} bins")
    return df


def fetch_bin_history(bin_id):
    """Fetch historical data for a specific bin"""
    # Get last N records
    ref = db.reference(f"/history/{bin_id}")
    # Limit to last 10 entries to calculate recent rate
    data = ref.order_by_key().limit_to_last(HISTORY_LIMIT).get()

    if not data:
        return {}
    return data


def compute_fill_rate_from_history(current_fill, current_time, history):
    """
    Calculate fill rate (percent per hour) based on history.
    FIXED: Handles String timestamps from Firebase.
    """
    if not history or len(history) < 2:
        return 0.5, 0, 0  # Default fallback rate

    # 1. Convert Dictionary to List of (Timestamp, Fill)
    points = []
    for ts_str, data in history.items():
        try:
            # FIX: Force convert String timestamp to Float
            ts = float(ts_str)
            fill = float(data.get("fill_level", 0))
            points.append((ts, fill))
        except ValueError:
            continue

    # Sort by time
    points.sort(key=lambda x: x[0])

    if len(points) < 2:
        return 0.5, 0, 0

    # 2. Calculate simple slope between oldest and newest point in this window
    start_time, start_fill = points[0]
    end_time, end_fill = points[-1]

    # Avoid division by zero
    if end_time == start_time:
        return 0.5, 0, 0

    # Calculate time difference in hours
    time_diff_hours = (end_time - start_time) / 3600.0
    fill_diff = end_fill - start_fill

    if time_diff_hours <= 0:
        return 0.5, 0, 0

    fill_rate = fill_diff / time_diff_hours

    # 3. Sanity check: If rate is negative (bin was emptied), reset to default
    if fill_rate < 0:
        fill_rate = 0.5  # Default slow fill rate

    return fill_rate, 0, 0


def prepare_features_for_prediction(bins_df):
    """Calculate fill rate for each bin"""
    print("Preparing features for prediction...")
    current_time = time.time()

    predictions = []

    for _, row in bins_df.iterrows():
        bin_id = row["bin_id"]
        current_fill = row["fill_level"]

        # Fetch history for this bin
        history = fetch_bin_history(bin_id)

        # Compute Rate
        fill_rate, _, _ = compute_fill_rate_from_history(
            current_fill, current_time, history
        )

        # Logic: How many hours until 100%?
        remaining_capacity = 100.0 - current_fill

        if remaining_capacity <= 0:
            time_to_full = 0
        elif fill_rate <= 0.1:
            # If filling very slowly, assume a long time (e.g., 24h+)
            time_to_full = 24.0
        else:
            time_to_full = remaining_capacity / fill_rate

        # Cap prediction at 48 hours to be realistic
        if time_to_full > 48:
            time_to_full = 48.0

        predictions.append(
            {
                "bin_id": bin_id,
                "fill_level": current_fill,
                "fill_rate": round(fill_rate, 2),
                "time_to_full_h": round(time_to_full, 1),
                "predicted_at": current_time,
            }
        )

    return pd.DataFrame(predictions)


def update_predictions_in_firebase(predictions_df):
    """Push results to Firebase"""
    print("Updating predictions in Firebase...")
    ref = db.reference("/predictions")

    updates = {}
    for _, row in predictions_df.iterrows():
        updates[row["bin_id"]] = {
            "fill_level": row["fill_level"],
            "fill_rate": row["fill_rate"],
            "time_to_full_h": row["time_to_full_h"],
            "predicted_at": row["predicted_at"],
        }

    ref.update(updates)
    print("Predictions updated successfully.")


def main():
    try:
        init_firebase()

        # 1. Get Current Data
        bins_df = fetch_current_bin_states()
        if bins_df.empty:
            print("No bins found.")
            return

        # 2. Predict logic (Simple Heuristic / Linear Regression)
        preds_df = prepare_features_for_prediction(bins_df)

        # 3. Save
        update_predictions_in_firebase(preds_df)

    except Exception as e:
        print(f"Error during inference: {e}")
        raise


if __name__ == "__main__":
    main()
