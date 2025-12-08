"""
Inference Script
Loads the trained model, reads current bin states from Firebase,
computes features, makes predictions, and writes results back to Firebase.
Designed to run as a cron job every few minutes.
"""

import pandas as pd
import numpy as np
import joblib
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import time

# Feature columns (must match training)
FEATURE_COLS = [
    "fill_level",
    "fill_rate",
    "fill_rate_rolling_mean",
    "fill_rate_rolling_std",
    "hour",
    "weekday",
    "is_weekend",
]


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


def load_model(model_path="models/time_to_full.joblib"):
    """Load the trained model"""
    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)
    print("Model loaded successfully")
    return model


def fetch_current_bins():
    """Fetch current bin states from /bins"""
    print("Fetching current bin states...")
    ref = db.reference("/bins")
    bins_data = ref.get()

    if not bins_data:
        print("No bin data found")
        return pd.DataFrame()

    # Convert to list of records
    records = []
    for bin_id, data in bins_data.items():
        record = {
            "bin_id": bin_id,
            "fill_level": data.get("fill_level", 0),
            "latitude": data.get("latitude", 0),
            "longitude": data.get("longitude", 0),
            "timestamp": data.get("timestamp", int(time.time())),
        }
        records.append(record)

    df = pd.DataFrame(records)
    print(f"Fetched {len(df)} bins")
    return df


def fetch_recent_history(bin_id, limit=5):
    """Fetch recent historical readings for a bin"""
    ref = db.reference(f"/history/{bin_id}")
    history = ref.order_by_key().limit_to_last(limit).get()

    if not history:
        return []

    records = []
    for timestamp, data in history.items():
        record = {"timestamp": int(timestamp), "fill_level": data.get("fill_level", 0)}
        records.append(record)

    return sorted(records, key=lambda x: x["timestamp"])


def compute_fill_rate_from_history(current_fill, current_time, history):
    """
    Compute fill rate from recent history.
    Returns fill_rate, rolling_mean, and rolling_std
    """
    if len(history) < 2:
        # Not enough history, use defaults
        return 0, 0, 0

    # Get last two readings to compute rate
    prev_reading = history[-1]
    prev_time = prev_reading["timestamp"]
    prev_fill = prev_reading["fill_level"]

    # Calculate time difference in hours
    time_diff_hours = (current_time - prev_time) / 3600

    if time_diff_hours <= 0:
        return 0, 0, 0

    # Calculate fill rate
    fill_diff = current_fill - prev_fill
    fill_rate = max(0, fill_diff / time_diff_hours)  # Clip negative rates

    # Compute rolling statistics from all available history
    rates = []
    for i in range(len(history) - 1):
        t1, f1 = history[i]["timestamp"], history[i]["fill_level"]
        t2, f2 = history[i + 1]["timestamp"], history[i + 1]["fill_level"]

        time_diff = (t2 - t1) / 3600
        if time_diff > 0:
            rate = max(0, (f2 - f1) / time_diff)
            rates.append(rate)

    # Add current rate
    rates.append(fill_rate)

    # Compute rolling statistics
    if len(rates) >= 3:
        rolling_mean = np.mean(rates[-3:])
        rolling_std = np.std(rates[-3:])
    else:
        rolling_mean = np.mean(rates)
        rolling_std = np.std(rates) if len(rates) > 1 else 0

    return fill_rate, rolling_mean, rolling_std


def compute_time_features(timestamp):
    """Extract time-based features from timestamp"""
    dt = datetime.fromtimestamp(timestamp)
    hour = dt.hour
    weekday = dt.weekday()
    is_weekend = 1 if weekday >= 5 else 0

    return hour, weekday, is_weekend


def prepare_features_for_prediction(bins_df):
    """
    Prepare features for prediction by fetching history and computing features
    """
    print("Preparing features for prediction...")

    features_list = []

    for idx, row in bins_df.iterrows():
        bin_id = row["bin_id"]
        current_fill = row["fill_level"]
        current_time = row["timestamp"]

        # Fetch recent history
        history = fetch_recent_history(bin_id, limit=5)

        # Compute fill rate features
        fill_rate, rolling_mean, rolling_std = compute_fill_rate_from_history(
            current_fill, current_time, history
        )

        # Compute time features
        hour, weekday, is_weekend = compute_time_features(current_time)

        # Build feature vector
        features = {
            "bin_id": bin_id,
            "fill_level": current_fill,
            "fill_rate": fill_rate,
            "fill_rate_rolling_mean": rolling_mean,
            "fill_rate_rolling_std": rolling_std,
            "hour": hour,
            "weekday": weekday,
            "is_weekend": is_weekend,
            "latitude": row["latitude"],
            "longitude": row["longitude"],
        }

        features_list.append(features)

    features_df = pd.DataFrame(features_list)
    print(f"Prepared features for {len(features_df)} bins")

    return features_df


def make_predictions(model, features_df):
    """Make predictions using the trained model"""
    print("Making predictions...")

    # Extract feature columns for prediction
    X = features_df[FEATURE_COLS].copy()

    # Handle any NaN or inf values
    X = X.fillna(0)
    X = X.replace([np.inf, -np.inf], 0)

    # Make predictions
    predictions = model.predict(X)

    # Add predictions to dataframe
    features_df["time_to_full_h"] = predictions

    # Clip predictions to reasonable range (0 to 168 hours = 1 week)
    features_df["time_to_full_h"] = features_df["time_to_full_h"].clip(0, 168)

    print(
        f"Predictions complete. Range: {predictions.min():.2f} - {predictions.max():.2f} hours"
    )

    return features_df


def write_predictions_to_firebase(predictions_df):
    """Write predictions back to Firebase at /predictions/<bin_id>"""
    print("Writing predictions to Firebase...")

    ref = db.reference("/predictions")
    current_timestamp = int(time.time())

    predictions_dict = {}
    for idx, row in predictions_df.iterrows():
        bin_id = row["bin_id"]
        predictions_dict[bin_id] = {
            "time_to_full_h": float(row["time_to_full_h"]),
            "predicted_at": current_timestamp,
            "fill_level": float(row["fill_level"]),
            "fill_rate": float(row["fill_rate"]),
        }

    # Write all predictions at once
    ref.set(predictions_dict)

    print(f"Successfully wrote predictions for {len(predictions_dict)} bins")

    # Print summary
    print("\n=== Prediction Summary ===")
    print(
        predictions_df[["bin_id", "fill_level", "time_to_full_h"]].to_string(
            index=False
        )
    )


def main():
    """Main inference pipeline"""
    try:
        start_time = time.time()

        # Initialize Firebase
        init_firebase()

        # Load model
        model = load_model()

        # Fetch current bin states
        bins_df = fetch_current_bins()

        if bins_df.empty:
            print("No bins to process")
            return

        # Prepare features
        features_df = prepare_features_for_prediction(bins_df)

        # Make predictions
        predictions_df = make_predictions(model, features_df)

        # Write predictions to Firebase
        write_predictions_to_firebase(predictions_df)

        elapsed = time.time() - start_time
        print(f"\n✓ Inference completed successfully in {elapsed:.2f} seconds")

    except Exception as e:
        print(f"Error during inference: {e}")
        raise


if __name__ == "__main__":
    main()
