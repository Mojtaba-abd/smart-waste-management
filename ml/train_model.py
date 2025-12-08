"""
Model Training Script
Trains a Random Forest Regressor to predict time_to_full_hours
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import json
from datetime import datetime

# Feature columns to use for training
FEATURE_COLS = [
    "fill_level",
    "fill_rate",
    "fill_rate_rolling_mean",
    "fill_rate_rolling_std",
    "hour",
    "weekday",
    "is_weekend",
]

TARGET_COL = "time_to_full_hours"


def load_data(data_path="data/prepared_data.csv"):
    """Load the prepared dataset"""
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records")
    return df


def prepare_features(df):
    """Prepare features and target for training"""
    print("Preparing features and target...")

    # Select feature columns
    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].copy()

    # Handle any remaining NaN values
    X = X.fillna(0)

    # Remove infinite values
    X = X.replace([np.inf, -np.inf], 0)

    print(f"Feature matrix shape: {X.shape}")
    print(f"Target shape: {y.shape}")

    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    """Split data into train and validation sets"""
    print(f"Splitting data (test_size={test_size})...")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    print(f"Training set: {len(X_train)} samples")
    print(f"Validation set: {len(X_val)} samples")

    return X_train, X_val, y_train, y_val


def train_model(X_train, y_train):
    """Train Random Forest Regressor"""
    print("\nTraining Random Forest Regressor...")

    # Initialize model with optimized hyperparameters
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=4,
        max_features="sqrt",
        n_jobs=-1,
        random_state=42,
        verbose=1,
    )

    # Train model
    model.fit(X_train, y_train)

    print("Training completed!")
    return model


def evaluate_model(model, X_train, y_train, X_val, y_val):
    """Evaluate model performance on train and validation sets"""
    print("\n=== Model Evaluation ===")

    # Predictions
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)

    # Training metrics
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    train_r2 = r2_score(y_train, y_train_pred)

    print("\nTraining Set Performance:")
    print(f"  MAE:  {train_mae:.2f} hours")
    print(f"  RMSE: {train_rmse:.2f} hours")
    print(f"  R²:   {train_r2:.4f}")

    # Validation metrics
    val_mae = mean_absolute_error(y_val, y_val_pred)
    val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
    val_r2 = r2_score(y_val, y_val_pred)

    print("\nValidation Set Performance:")
    print(f"  MAE:  {val_mae:.2f} hours")
    print(f"  RMSE: {val_rmse:.2f} hours")
    print(f"  R²:   {val_r2:.4f}")

    # Feature importance
    feature_importance = pd.DataFrame(
        {"feature": FEATURE_COLS, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)

    print("\nFeature Importance:")
    for idx, row in feature_importance.iterrows():
        print(f"  {row['feature']:25s}: {row['importance']:.4f}")

    # Return metrics
    metrics = {
        "train_mae": float(train_mae),
        "train_rmse": float(train_rmse),
        "train_r2": float(train_r2),
        "val_mae": float(val_mae),
        "val_rmse": float(val_rmse),
        "val_r2": float(val_r2),
        "feature_importance": feature_importance.to_dict("records"),
    }

    return metrics


def save_model(model, metrics, model_path="models/time_to_full.joblib"):
    """Save trained model and metadata"""
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Save model
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")

    # Save metadata
    metadata = {
        "trained_at": datetime.now().isoformat(),
        "feature_columns": FEATURE_COLS,
        "target_column": TARGET_COL,
        "model_type": "RandomForestRegressor",
        "metrics": metrics,
    }

    metadata_path = model_path.replace(".joblib", "_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata saved to {metadata_path}")


def main():
    """Main training pipeline"""
    try:
        # Load data
        df = load_data()

        # Prepare features
        X, y = prepare_features(df)

        # Split data
        X_train, X_val, y_train, y_val = split_data(X, y)

        # Train model
        model = train_model(X_train, y_train)

        # Evaluate model
        metrics = evaluate_model(model, X_train, y_train, X_val, y_val)

        # Save model
        save_model(model, metrics)

        print("\n✓ Model training completed successfully!")

    except Exception as e:
        print(f"Error during training: {e}")
        raise


if __name__ == "__main__":
    main()
