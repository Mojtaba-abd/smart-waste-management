"""
Live Data Simulation Script (FAST MODE)
Adds specific area assignment to bins.
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
UPDATE_INTERVAL = 1.0  # seconds between updates
COLLECTION_CHECK_INTERVAL = 20  # seconds between checking for collections

# Geographic boundaries (Baghdad area example)
LAT_MIN, LAT_MAX = 33.2, 33.4
LON_MIN, LON_MAX = 44.3, 44.5

# CHANGED: Define specific collection areas
AREAS = ["Central", "North", "South", "East", "West"]

# Fill rate profiles (percentage increase per update interval)
FILL_PROFILES = {
    "residential_high": (2.0, 4.0),
    "residential_low": (1.0, 2.0),
    "commercial": (3.0, 7.0),
    "park": (0.5, 1.5),
    "industrial": (1.5, 3.5),
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

        # CHANGED: Assign a random area
        area = random.choice(AREAS)

        # Random profile and starting fill level
        profile = random.choice(profiles)
        fill_level = random.uniform(0, 60)

        bin_state = {
            "bin_id": bin_id,
            "latitude": lat,
            "longitude": lon,
            "area": area,  # ADDED: Area field
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

    # Peak hours (meal times)
    if 7 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 21:
        modifier *= random.uniform(1.3, 1.8)

    # Night hours
    elif 22 <= hour or hour <= 6:
        modifier *= random.uniform(0.5, 0.8)

    # Weekend variation
    if weekday >= 5:
        modifier *= random.uniform(1.1, 1.4)

    # Random variation
    modifier *= random.uniform(0.85, 1.15)

    return modifier


def should_collect_bin(bin_state):
    """Determine if bin should be collected"""
    if bin_state["fill_level"] >= 98:
        return True
    return False


def collect_bin(bin_state):
    """Simulate bin collection"""
    bin_state["fill_level"] = random.uniform(0, 5)
    bin_state["last_collection"] = int(time.time())
    bin_state["total_collections"] += 1
    return True


def update_bin(bin_state):
    """Update a single bin's fill level"""
    fill_rate = bin_state["base_fill_rate"] * calculate_fill_rate_modifier()
    bin_state["fill_level"] += fill_rate
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
        "area": bin_state["area"],  # ADDED: Write area to /bins
        "timestamp": timestamp,
    }
    bins_ref.set(current_data)

    # Historical data to /history
    if write_history:
        day_key = str(datetime.now().day)
        history_ref = db.reference(f"/history/{day_key}/{bin_id}/{timestamp}")
        history_ref.set(current_data)


def print_status(bins_state, collections_this_round):
    """Print current status of all bins"""
    os.system("clear" if sys.platform != "win32" else "cls")

    print("=" * 80)
    print("🚀 FAST LIVE WASTE BIN SIMULATION")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Active Bins: {len(bins_state)}")
    print(f"Update Interval: {UPDATE_INTERVAL}s")
    print(f"Collections This Round: {collections_this_round}")
    print("=" * 80)

    # ... (rest of print_status remains the same) ...

    # Sort bins by fill level (highest first)
    sorted_bins = sorted(bins_state, key=lambda x: x["fill_level"], reverse=True)

    # Print header
    print(
        f"{'Bin ID':<12} {'Fill %':<10} {'Area':<10} {'Profile':<15} {'Collections':<12} {'Status'}"
    )
    print("-" * 80)

    for bin_state in sorted_bins:
        fill_level = bin_state["fill_level"]

        if fill_level >= 90:
            status = "🔴 CRITICAL"
        elif fill_level >= 70:
            status = "🟠 HIGH"
        elif fill_level >= 50:
            status = "🟡 MEDIUM"
        else:
            status = "🟢 LOW"

        bar_length = 20
        filled = int((fill_level / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(
            f"{bin_state['bin_id']:<12} "
            f"{fill_level:>5.1f}% {bar} "
            f"{bin_state['area']:<10} "  # ADDED: Print Area
            f"{bin_state['profile']:<15} "
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

    signal.signal(signal.SIGINT, signal_handler)

    try:
        print("🚀 Starting FAST Live Waste Bin Simulation...")
        init_firebase()
        print("✓ Connected to Firebase")

        bins_state = generate_bins(NUM_BINS)
        print(f"✓ Generated {NUM_BINS} bins")

        print("✓ Writing initial states to Firebase...")
        for bin_state in bins_state:
            write_to_firebase(bin_state, write_history=True)

        print("✓ Simulation started!")
        time.sleep(1)

        iteration = 0
        last_collection_check = time.time()

        while running:
            iteration += 1
            collections_this_round = 0

            for bin_state in bins_state:
                current_time = time.time()
                if (current_time - last_collection_check) >= COLLECTION_CHECK_INTERVAL:
                    if should_collect_bin(bin_state):
                        old_fill = bin_state["fill_level"]
                        collect_bin(bin_state)
                        collections_this_round += 1
                        print_collection_event(bin_state["bin_id"], old_fill)

                update_bin(bin_state)
                write_to_firebase(bin_state, write_history=(iteration % 10 == 0))

            if (time.time() - last_collection_check) >= COLLECTION_CHECK_INTERVAL:
                last_collection_check = time.time()

            print_status(bins_state, collections_this_round)
            time.sleep(UPDATE_INTERVAL)

        print("\n✓ Simulation stopped gracefully")

    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        raise


if __name__ == "__main__":
    main()
