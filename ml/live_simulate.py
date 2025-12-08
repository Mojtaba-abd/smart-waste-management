"""
Live Data Simulation Script
Continuously simulates ESP32 devices sending real-time bin data to Firebase.
Updates bins every few seconds to mimic actual waste accumulation.
"""

import os
import sys
import time
import random
import signal
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Configuration
NUM_BINS = 25
UPDATE_INTERVAL = 3  # seconds between updates
COLLECTION_CHECK_INTERVAL = 60  # seconds between checking for collections

# Geographic boundaries (Baghdad area example)
LAT_MIN, LAT_MAX = 33.2, 33.4
LON_MIN, LON_MAX = 44.3, 44.5

# Fill rate profiles (percentage increase per update interval)
FILL_PROFILES = {
    "residential_high": (0.5, 1.5),  # Fast filling
    "residential_low": (0.2, 0.6),  # Moderate filling
    "commercial": (1.0, 2.5),  # Very fast
    "park": (0.1, 0.4),  # Slow filling
    "industrial": (0.4, 1.0),  # Moderate to fast
}

# Global state
running = True
bins_state = []


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n\n🛑 Stopping simulation...")
    running = False


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


def generate_bins(num_bins):
    """Generate initial bin states"""
    bins = []
    profiles = list(FILL_PROFILES.keys())

    for i in range(num_bins):
        bin_id = f"bin_{i+1:03d}"

        # Random location
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lon = random.uniform(LON_MIN, LON_MAX)

        # Random profile and starting fill level
        profile = random.choice(profiles)
        fill_level = random.uniform(0, 40)  # Start with 0-40% full

        bin_state = {
            "bin_id": bin_id,
            "latitude": lat,
            "longitude": lon,
            "profile": profile,
            "base_fill_rate": random.uniform(*FILL_PROFILES[profile]),
            "fill_level": fill_level,
            "last_collection": int(time.time()),
            "total_collections": 0,
        }

        bins.append(bin_state)

    return bins


def calculate_fill_rate_modifier():
    """Calculate fill rate modifier based on current time"""
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()

    modifier = 1.0

    # Peak hours (meal times) - more waste
    if 7 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 21:
        modifier *= random.uniform(1.3, 1.8)

    # Night hours - less waste
    elif 22 <= hour or hour <= 6:
        modifier *= random.uniform(0.2, 0.5)

    # Weekend variation
    if weekday >= 5:
        modifier *= random.uniform(1.1, 1.4)

    # Random variation
    modifier *= random.uniform(0.85, 1.15)

    return modifier


def should_collect_bin(bin_state):
    """Determine if bin should be collected"""
    # Collect if very full
    if bin_state["fill_level"] >= 95:
        return True

    # Probabilistic collection for bins 80-95% full
    if bin_state["fill_level"] >= 80:
        collection_prob = (bin_state["fill_level"] - 80) / 15 * 0.5
        return random.random() < collection_prob

    return False


def collect_bin(bin_state):
    """Simulate bin collection"""
    bin_state["fill_level"] = random.uniform(0, 5)  # Nearly empty after collection
    bin_state["last_collection"] = int(time.time())
    bin_state["total_collections"] += 1
    return True


def update_bin(bin_state):
    """Update a single bin's fill level"""
    # Calculate fill rate with time-based modifiers
    fill_rate = bin_state["base_fill_rate"] * calculate_fill_rate_modifier()

    # Update fill level
    bin_state["fill_level"] += fill_rate

    # Cap at 100%
    bin_state["fill_level"] = min(100, bin_state["fill_level"])

    return bin_state


def write_to_firebase(bin_state, write_history=True):
    """Write bin data to Firebase"""
    bin_id = bin_state["bin_id"]
    timestamp = int(time.time())

    # Current state to /bins
    bins_ref = db.reference(f"/bins/{bin_id}")
    current_data = {
        "fill_level": round(bin_state["fill_level"], 2),
        "latitude": round(bin_state["latitude"], 6),
        "longitude": round(bin_state["longitude"], 6),
        "timestamp": timestamp,
    }
    bins_ref.set(current_data)

    # Historical data to /history
    if write_history:
        history_ref = db.reference(f"/history/{bin_id}/{timestamp}")
        history_ref.set(current_data)


def print_status(bins_state, collections_this_round):
    """Print current status of all bins"""
    os.system("clear" if sys.platform != "win32" else "cls")

    print("=" * 80)
    print("🚮 LIVE WASTE BIN SIMULATION")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Active Bins: {len(bins_state)}")
    print(f"Update Interval: {UPDATE_INTERVAL}s")
    print(f"Collections This Round: {collections_this_round}")
    print("=" * 80)
    print()

    # Sort bins by fill level (highest first)
    sorted_bins = sorted(bins_state, key=lambda x: x["fill_level"], reverse=True)

    # Print header
    print(
        f"{'Bin ID':<12} {'Fill %':<10} {'Profile':<18} {'Collections':<12} {'Status'}"
    )
    print("-" * 80)

    for bin_state in sorted_bins:
        fill_level = bin_state["fill_level"]

        # Status indicator
        if fill_level >= 90:
            status = "🔴 CRITICAL"
        elif fill_level >= 70:
            status = "🟠 HIGH"
        elif fill_level >= 50:
            status = "🟡 MEDIUM"
        else:
            status = "🟢 LOW"

        # Fill level bar
        bar_length = 20
        filled = int((fill_level / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(
            f"{bin_state['bin_id']:<12} "
            f"{fill_level:>5.1f}% {bar} "
            f"{bin_state['profile']:<18} "
            f"{bin_state['total_collections']:<12} "
            f"{status}"
        )

    print()
    print("=" * 80)
    print("Press Ctrl+C to stop simulation")
    print("=" * 80)


def print_collection_event(bin_id, fill_level):
    """Print collection event notification"""
    print(f"\n🚛 COLLECTION EVENT: {bin_id} collected at {fill_level:.1f}% full")


def main():
    """Main live simulation loop"""
    global running, bins_state

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    try:
        print("🚀 Starting Live Waste Bin Simulation...")
        print()

        # Initialize Firebase
        init_firebase()
        print("✓ Connected to Firebase")

        # Generate bins
        bins_state = generate_bins(NUM_BINS)
        print(f"✓ Generated {NUM_BINS} bins")

        # Write initial states
        print("✓ Writing initial states to Firebase...")
        for bin_state in bins_state:
            write_to_firebase(bin_state, write_history=True)

        print("✓ Simulation started!")
        print()
        time.sleep(2)

        # Main simulation loop
        iteration = 0
        last_collection_check = time.time()

        while running:
            iteration += 1
            collections_this_round = 0

            # Update all bins
            for bin_state in bins_state:
                # Check for collection
                current_time = time.time()
                if (current_time - last_collection_check) >= COLLECTION_CHECK_INTERVAL:
                    if should_collect_bin(bin_state):
                        old_fill = bin_state["fill_level"]
                        collect_bin(bin_state)
                        collections_this_round += 1
                        print_collection_event(bin_state["bin_id"], old_fill)

                # Update fill level
                update_bin(bin_state)

                # Write to Firebase
                write_to_firebase(bin_state, write_history=(iteration % 6 == 0))

            # Update last collection check time
            if (time.time() - last_collection_check) >= COLLECTION_CHECK_INTERVAL:
                last_collection_check = time.time()

            # Print status
            print_status(bins_state, collections_this_round)

            # Wait before next update
            time.sleep(UPDATE_INTERVAL)

        print("\n✓ Simulation stopped gracefully")
        print(f"Total iterations: {iteration}")

    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        raise


if __name__ == "__main__":
    main()
