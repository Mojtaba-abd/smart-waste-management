"""
Smart Waste Management - Live Data Simulation
Generates real-time sensor data for demo purposes.
Simulates bin fill levels, rapid updates, and collection events.
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

# --- Configuration ---
NUM_BINS = 26  # Matches your physical bin count + virtual ones
UPDATE_INTERVAL = 1.0  # Seconds between sensor readings
COLLECTION_CHECK_INTERVAL = 20  # Seconds between "truck" visits

# Geographic boundaries (Baghdad, Iraq)
LAT_MIN, LAT_MAX = 33.2, 33.4
LON_MIN, LON_MAX = 44.3, 44.5

# Fill rate profiles (How fast bins fill up based on location type)
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
    """Handle Ctrl+C gracefully to stop the demo"""
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
    """Generate initial bin states with random locations and types"""
    bins = []
    profiles = list(FILL_PROFILES.keys())

    for i in range(num_bins):
        bin_id = f"bin_{i+1:03d}"

        # Random geographic location
        lat = random.uniform(LAT_MIN, LAT_MAX)
        lon = random.uniform(LON_MIN, LON_MAX)

        # Random usage profile
        profile = random.choice(profiles)
        fill_level = random.uniform(0, 60) # Start with random fill

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
    """Simulate time-of-day impact on waste generation"""
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()

    modifier = 1.0

    # Rush Hours (High waste generation)
    if 7 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 21:
        modifier *= random.uniform(1.3, 1.8)

    # Night Time (Low waste generation)
    elif 22 <= hour or hour <= 6:
        modifier *= random.uniform(0.5, 0.8)

    # Weekend Spike
    if weekday >= 5:
        modifier *= random.uniform(1.1, 1.4)

    return modifier * random.uniform(0.85, 1.15)

def should_collect_bin(bin_state):
    """Determine if a bin is full enough to require collection"""
    return bin_state["fill_level"] >= 98

def collect_bin(bin_state):
    """Simulate a truck emptying the bin"""
    bin_state["fill_level"] = random.uniform(0, 5) # Not perfectly empty
    bin_state["last_collection"] = int(time.time())
    bin_state["total_collections"] += 1
    return True

def update_bin(bin_state):
    """Increment fill level based on profile and time"""
    fill_rate = bin_state["base_fill_rate"] * calculate_fill_rate_modifier()
    bin_state["fill_level"] += fill_rate
    bin_state["fill_level"] = min(100, bin_state["fill_level"])
    return bin_state

def write_to_firebase(bin_state, write_history=True):
    """Push updates to Firebase Realtime Database"""
    bin_id = bin_state["bin_id"]
    timestamp = int(time.time())

    # Update Live State
    bins_ref = db.reference(f"/bins/{bin_id}")
    current_data = {
        "fill_level": round(bin_state["fill_level"], 2),
        "latitude": round(bin_state["latitude"], 6),
        "longitude": round(bin_state["longitude"], 6),
        "timestamp": timestamp,
    }
    bins_ref.set(current_data)

    # Record History (for ML Training)
    if write_history:
        day_key = str(datetime.now().day)
        history_ref = db.reference(f"/history/{day_key}/{bin_id}/{timestamp}")
        history_ref.set(current_data)

def print_status(bins_state, collections_this_round):
    """Display a professional dashboard in the terminal"""
    os.system("clear" if sys.platform != "win32" else "cls")

    print("=" * 80)
    print("🚀 TEAM ENKI - LIVE SENSOR SIMULATION")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')} | Update Rate: {UPDATE_INTERVAL}s")
    print(f"Active Nodes: {len(bins_state)} | Collections Run: {collections_this_round}")
    print("=" * 80)

    # Sort by fill level (Critical first)
    sorted_bins = sorted(bins_state, key=lambda x: x["fill_level"], reverse=True)

    print(f"{'Bin ID':<10} {'Fill %':<10} {'Status':<15} {'Visual':<25} {'Profile'}")
    print("-" * 80)

    for bin_state in sorted_bins[:15]: # Show top 15 only to fit screen
        fill_level = bin_state["fill_level"]

        if fill_level >= 90:
            status = "🔴 CRITICAL"
        elif fill_level >= 70:
            status = "🟠 WARNING"
        elif fill_level >= 50:
            status = "🟡 NORMAL"
        else:
            status = "🟢 LOW"

        bar_length = 20
        filled = int((fill_level / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(
            f"{bin_state['bin_id']:<10} "
            f"{fill_level:>5.1f}%     "
            f"{status:<15} "
            f"{bar}   "
            f"{bin_state['profile']}"
        )

    print("-" * 80)
    print("Press Ctrl+C to stop simulation")

def main():
    """Main execution loop"""
    global running, bins_state

    signal.signal(signal.SIGINT, signal_handler)

    try:
        print("\n🚀 Initializing Simulation Environment...")
        init_firebase()
        print("✓ Firebase Connected")

        bins_state = generate_bins(NUM_BINS)
        print(f"✓ {NUM_BINS} Virtual Nodes Generated")

        print("✓ Pushing initial state...")
        for bin_state in bins_state:
            write_to_firebase(bin_state, write_history=True)

        print("✓ Starting Live Loop...")
        time.sleep(1)

        iteration = 0
        last_collection_check = time.time()

        while running:
            iteration += 1
            collections_this_round = 0

            # Update every bin
            for bin_state in bins_state:
                current_time = time.time()
                
                # Check for "Truck Collection" events periodically
                if (current_time - last_collection_check) >= COLLECTION_CHECK_INTERVAL:
                    if should_collect_bin(bin_state):
                        collect_bin(bin_state)
                        collections_this_round += 1

                # Simulate sensor reading update
                update_bin(bin_state)
                
                # Write to DB (Record history less frequently to save space)
                write_to_firebase(bin_state, write_history=(iteration % 10 == 0))

            if (time.time() - last_collection_check) >= COLLECTION_CHECK_INTERVAL:
                last_collection_check = time.time()

            print_status(bins_state, collections_this_round)
            time.sleep(UPDATE_INTERVAL)

        print("\n✓ Simulation stopped gracefully.")

    except Exception as e:
        print(f"\n❌ Simulation Error: {e}")
        raise

if __name__ == "__main__":
    main()