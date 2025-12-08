"""
Data Simulation Script
Generates realistic simulated waste bin data and writes it to Firebase.
Creates historical data and current bin states for testing the entire pipeline.
"""

import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import time
import random

# Configuration
NUM_BINS = 25
DAYS_OF_HISTORY = 30
READINGS_PER_DAY = 24  # One reading per hour

# Geographic boundaries (Baghdad area example)
LAT_MIN, LAT_MAX = 33.2, 33.4
LON_MIN, LON_MAX = 44.3, 44.5

# Fill rate profiles (percentage increase per hour)
FILL_PROFILES = {
    "residential_high": (2.0, 4.0),  # Fast filling (busy residential)
    "residential_low": (1.0, 2.0),  # Moderate filling
    "commercial": (3.0, 6.0),  # Very fast (restaurants, shops)
    "park": (0.5, 1.5),  # Slow filling
    "industrial": (1.5, 3.0),  # Moderate to fast
}


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


def generate_bin_metadata(num_bins):
    """Generate metadata for bins"""
    bins = []
    profiles = list(FILL_PROFILES.keys())

    for i in range(num_bins):
        bin_id = f"bin_{i+1:03d}"

        # Random location
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lon = random.uniform(LON_MIN, LON_MAX)

        # Random profile
        profile = random.choice(profiles)

        bin_meta = {
            "bin_id": bin_id,
            "latitude": lat,
            "longitude": lon,
            "profile": profile,
            "base_fill_rate": random.uniform(*FILL_PROFILES[profile]),
        }

        bins.append(bin_meta)

    return bins


def add_noise_to_fill_rate(base_rate, hour, weekday):
    """Add realistic variations based on time"""
    rate = base_rate

    # Peak hours variation (more waste during meal times)
    if 7 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 21:
        rate *= random.uniform(1.2, 1.5)

    # Night hours (less waste)
    if 22 <= hour or hour <= 6:
        rate *= random.uniform(0.3, 0.6)

    # Weekend variation (residential areas have more waste)
    if weekday >= 5:
        rate *= random.uniform(1.1, 1.3)

    # Random noise
    rate *= random.uniform(0.8, 1.2)

    return max(0, rate)


def simulate_bin_collection(fill_level):
    """Simulate bin collection (emptying)"""
    # When bin is >85% full, there's a chance it gets collected
    if fill_level > 85:
        collection_probability = min(0.7, (fill_level - 85) / 15 * 0.7)
        if random.random() < collection_probability:
            return True
    return False


def generate_historical_data(bin_meta, days=DAYS_OF_HISTORY):
    """Generate historical time series data for a bin"""
    history = []

    # Start from N days ago
    start_time = datetime.now() - timedelta(days=days)
    current_fill = random.uniform(0, 30)  # Starting fill level

    for day in range(days):
        for hour in range(24):
            timestamp = start_time + timedelta(days=day, hours=hour)
            unix_timestamp = int(timestamp.timestamp())
            weekday = timestamp.weekday()

            # Simulate collection
            if simulate_bin_collection(current_fill):
                current_fill = random.uniform(0, 10)  # After collection

            # Calculate fill rate for this hour
            fill_rate = add_noise_to_fill_rate(
                bin_meta["base_fill_rate"], hour, weekday
            )

            # Update fill level
            current_fill += fill_rate
            current_fill = min(100, current_fill)  # Cap at 100%

            # Record data
            reading = {
                "timestamp": unix_timestamp,
                "fill_level": round(current_fill, 2),
                "latitude": bin_meta["latitude"],
                "longitude": bin_meta["longitude"],
            }

            history.append(reading)

    return history, current_fill


def write_to_firebase(bins_metadata, historical_data):
    """Write simulated data to Firebase"""
    print("Writing data to Firebase...")

    # Write historical data
    history_ref = db.reference("/history")
    bins_ref = db.reference("/bins")

    for bin_meta, (history, current_fill) in zip(bins_metadata, historical_data):
        bin_id = bin_meta["bin_id"]

        print(f"Writing {bin_id}: {len(history)} historical readings")

        # Write historical readings
        bin_history = {}
        for reading in history:
            timestamp_str = str(reading["timestamp"])
            bin_history[timestamp_str] = {
                "fill_level": reading["fill_level"],
                "latitude": reading["latitude"],
                "longitude": reading["longitude"],
            }

        history_ref.child(bin_id).set(bin_history)

        # Write current bin state (most recent reading)
        latest = history[-1]
        bins_ref.child(bin_id).set(
            {
                "fill_level": latest["fill_level"],
                "latitude": latest["latitude"],
                "longitude": latest["longitude"],
                "timestamp": latest["timestamp"],
            }
        )

    print(f"\n✓ Successfully wrote data for {len(bins_metadata)} bins to Firebase")


def print_summary(bins_metadata, historical_data):
    """Print summary statistics"""
    print("\n=== SIMULATION SUMMARY ===")
    print(f"Total bins: {len(bins_metadata)}")
    print(f"Days of history: {DAYS_OF_HISTORY}")
    print(f"Readings per bin: {len(historical_data[0][0])}")
    print(f"Total readings: {len(bins_metadata) * len(historical_data[0][0])}")

    print("\nBin Profiles:")
    profile_counts = {}
    for bin_meta in bins_metadata:
        profile = bin_meta["profile"]
        profile_counts[profile] = profile_counts.get(profile, 0) + 1

    for profile, count in sorted(profile_counts.items()):
        print(f"  {profile}: {count} bins")

    print("\nCurrent Fill Levels:")
    fill_levels = [data[1] for data in historical_data]
    print(f"  Min: {min(fill_levels):.1f}%")
    print(f"  Max: {max(fill_levels):.1f}%")
    print(f"  Mean: {np.mean(fill_levels):.1f}%")
    print(f"  Median: {np.median(fill_levels):.1f}%")

    urgent_bins = sum(1 for fl in fill_levels if fl > 80)
    print(f"\nBins > 80% full: {urgent_bins}")


def main():
    """Main simulation function"""
    try:
        print("=== WASTE BIN DATA SIMULATOR ===\n")

        # Initialize Firebase
        init_firebase()

        # Generate bin metadata
        print(f"Generating metadata for {NUM_BINS} bins...")
        bins_metadata = generate_bin_metadata(NUM_BINS)

        # Generate historical data for each bin
        print(f"Generating {DAYS_OF_HISTORY} days of historical data...")
        historical_data = []

        for i, bin_meta in enumerate(bins_metadata):
            print(f"  Simulating {bin_meta['bin_id']} ({i+1}/{NUM_BINS})...", end="\r")
            history, current_fill = generate_historical_data(bin_meta)
            historical_data.append((history, current_fill))

        print(f"\nGenerated {len(historical_data)} bin histories")

        # Write to Firebase
        write_to_firebase(bins_metadata, historical_data)

        # Print summary
        print_summary(bins_metadata, historical_data)

        print("\n✓ Simulation complete! You can now run:")
        print("  1. python data_prep.py")
        print("  2. python train_model.py")
        print("  3. python inference.py")
        print("  4. python routing.py")

    except Exception as e:
        print(f"\nError during simulation: {e}")
        raise


if __name__ == "__main__":
    main()
