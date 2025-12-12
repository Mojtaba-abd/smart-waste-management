"""
Route Optimization Module (Simple & Robust)
Selects the most urgent bins (Physical Fill > 80% OR Predicted Full < 12h)
and calculates a route starting from the Depot.
"""

import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import time
from math import radians, cos, sin, asin, sqrt

# Configuration
DEPOT_LAT = 33.5731
DEPOT_LON = 44.3668
TIME_THRESHOLD = 12  # Prediction urgency threshold
FILL_THRESHOLD = 80  # Physical fill urgency threshold
MAX_BINS_PER_ROUTE = 20  # Truck capacity


def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://smart-waste-3d7d0-default-rtdb.europe-west1.firebasedatabase.app/"
            },
        )


def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


def fetch_predictions():
    print("Fetching predictions...")
    ref = db.reference("/predictions")
    data = ref.get()
    if not data:
        return pd.DataFrame()

    records = []
    for bin_id, d in data.items():
        records.append(
            {
                "bin_id": bin_id,
                "time_to_full_h": d.get("time_to_full_h", 999),
                "fill_level": d.get("fill_level", 0),
            }
        )
    return pd.DataFrame(records)


def fetch_bin_locations(bin_ids):
    print("Fetching locations...")
    locations = []
    ref = db.reference("/bins")
    for bin_id in bin_ids:
        d = ref.child(bin_id).get()
        if d:
            locations.append(
                {
                    "bin_id": bin_id,
                    "latitude": d.get("latitude", 0),
                    "longitude": d.get("longitude", 0),
                }
            )
    return pd.DataFrame(locations)


def select_bins(predictions_df, locations_df):
    """
    Simple Selection Logic:
    1. Filter bins that are > 80% full OR < 12h to full.
    2. If too many, pick the ones with highest fill level.
    """
    # Merge data
    df = pd.merge(predictions_df, locations_df, on="bin_id", how="inner")

    # Filter for urgency
    urgent_mask = (df["fill_level"] >= FILL_THRESHOLD) | (
        df["time_to_full_h"] <= TIME_THRESHOLD
    )
    urgent_bins = df[urgent_mask].copy()

    # Fallback: If nothing is "urgent", pick the top 5 fullest bins just to show a route exists
    if urgent_bins.empty:
        print("🟡 No critical bins found. Picking top 5 fullest bins for demo.")
        urgent_bins = df.nlargest(5, "fill_level")

    # Cap at Max Bins (prioritize physical fill level)
    if len(urgent_bins) > MAX_BINS_PER_ROUTE:
        urgent_bins = urgent_bins.nlargest(MAX_BINS_PER_ROUTE, "fill_level")

    print(f"✅ Selected {len(urgent_bins)} bins for routing.")
    return urgent_bins


def create_distance_matrix(locations_df):
    coords = [(DEPOT_LAT, DEPOT_LON)]
    for _, row in locations_df.iterrows():
        coords.append((row["latitude"], row["longitude"]))

    n = len(coords)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = (
                    haversine_distance(
                        coords[i][0], coords[i][1], coords[j][0], coords[j][1]
                    )
                    * 1000
                )
    return matrix.astype(int)


def solve_tsp(matrix):
    print("Solving TSP...")
    manager = pywrapcp.RoutingIndexManager(len(matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def dist_callback(i, j):
        return matrix[manager.IndexToNode(i)][manager.IndexToNode(j)]

    transit_idx = routing.RegisterTransitCallback(dist_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    params.time_limit.seconds = 10

    solution = routing.SolveWithParameters(params)
    if not solution:
        return None, 0

    route = []
    index = routing.Start(0)
    total_dist = 0
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        prev = index
        index = solution.Value(routing.NextVar(index))
        total_dist += routing.GetArcCostForVehicle(prev, index, 0)

    route.append(manager.IndexToNode(index))
    return route, total_dist


def save_route(route, locations_df, predictions_df):
    print("Saving to Firebase...")
    stops = []
    total_dist = 0

    for i, idx in enumerate(route):
        if idx == 0:
            stops.append(
                {
                    "order": i,
                    "type": "depot",
                    "latitude": DEPOT_LAT,
                    "longitude": DEPOT_LON,
                    "bin_id": "DEPOT",
                }
            )
        else:
            row = locations_df.iloc[idx - 1]
            pred = predictions_df[predictions_df["bin_id"] == row["bin_id"]].iloc[0]

            # Calculate distance from previous stop
            dist_from_prev = 0
            if i > 0:
                prev = stops[-1]
                dist_from_prev = haversine_distance(
                    prev["latitude"],
                    prev["longitude"],
                    row["latitude"],
                    row["longitude"],
                )
                total_dist += dist_from_prev

            stops.append(
                {
                    "order": i,
                    "type": "bin",
                    "bin_id": row["bin_id"],
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "fill_level": float(pred["fill_level"]),
                    "dist_km": round(dist_from_prev, 2),
                }
            )

    route_data = {
        "stops": stops,
        "total_distance_km": round(total_dist, 2),
        "total_bins": len(stops) - 2,  # Exclude start/end depot
        "created_at": int(time.time()),
    }

    # Save to route_1 so dashboard finds it easily
    db.reference("/routes/route_1").set(route_data)
    print("✓ Route saved to /routes/route_1")


def main():
    try:
        init_firebase()
        preds = fetch_predictions()
        if preds.empty:
            return {"status": "error", "message": "No predictions"}

        # Select all bins needed for routing
        all_locs = fetch_bin_locations(preds["bin_id"].tolist())
        selected = select_bins(preds, all_locs)

        if len(selected) < 1:
            return {"status": "success", "message": "No bins need collection"}

        matrix = create_distance_matrix(selected)
        route, _ = solve_tsp(matrix)

        if route:
            save_route(route, selected, preds)
            return {"status": "success"}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    main()
