"""
Route Optimization Module
Reads predictions from Firebase, selects bins that need collection,
computes optimal collection route using Google OR-Tools TSP solver,
and writes route back to Firebase.
"""

import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import time
import json
from math import radians, cos, sin, asin, sqrt

# Depot location (Baghdad example)
DEPOT_LAT = 33.5731
DEPOT_LON = 44.3668

# Threshold for urgent collection (hours)
TIME_THRESHOLD = 12
MAX_BINS_PER_ROUTE = 20

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

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers
    return c * r

def fetch_predictions():
    """Fetch all predictions from Firebase"""
    print("Fetching predictions from Firebase...")
    ref = db.reference("/predictions")
    predictions = ref.get()

    if not predictions:
        print("No predictions found")
        return pd.DataFrame()

    records = []
    for bin_id, data in predictions.items():
        record = {
            "bin_id": bin_id,
            "time_to_full_h": data.get("time_to_full_h", 999),
            "fill_level": data.get("fill_level", 0),
            "predicted_at": data.get("predicted_at", 0),
        }
        records.append(record)

    df = pd.DataFrame(records)
    print(f"Fetched predictions for {len(df)} bins")
    return df

def fetch_bin_locations(bin_ids):
    """Fetch location data for specific bins"""
    print(f"Fetching locations for {len(bin_ids)} bins...")
    locations = []
    ref = db.reference("/bins")

    for bin_id in bin_ids:
        bin_data = ref.child(bin_id).get()
        if bin_data:
            locations.append({
                "bin_id": bin_id,
                "latitude": bin_data.get("latitude", 0),
                "longitude": bin_data.get("longitude", 0),
            })

    return pd.DataFrame(locations)

def select_bins_for_collection(predictions_df, threshold=TIME_THRESHOLD, max_bins=MAX_BINS_PER_ROUTE):
    """Select bins based on urgency"""
    print(f"\nSelecting bins with time_to_full <= {threshold} hours...")
    
    urgent_bins = predictions_df[predictions_df["time_to_full_h"] <= threshold].copy()

    if len(urgent_bins) == 0:
        print(f"No urgent bins found. Selecting top {max_bins} almost full bins...")
        urgent_bins = predictions_df.nsmallest(max_bins, "time_to_full_h").copy()
    elif len(urgent_bins) > max_bins:
        print(f"Found {len(urgent_bins)} urgent bins. Selecting {max_bins} most urgent...")
        urgent_bins = urgent_bins.nsmallest(max_bins, "time_to_full_h")

    urgent_bins = urgent_bins.sort_values("time_to_full_h")
    print(f"Selected {len(urgent_bins)} bins for collection")
    return urgent_bins

def create_distance_matrix(locations_df):
    """Create distance matrix in meters"""
    print("\nCreating distance matrix...")
    coords = [(DEPOT_LAT, DEPOT_LON)]
    for idx, row in locations_df.iterrows():
        coords.append((row["latitude"], row["longitude"]))

    n = len(coords)
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lon1 = coords[i]
                lat2, lon2 = coords[j]
                distance_matrix[i][j] = haversine_distance(lat1, lon1, lat2, lon2) * 1000

    print(f"Distance matrix created: {n}x{n} locations")
    return distance_matrix.astype(int)

def solve_tsp(distance_matrix):
    """Solve TSP using OR-Tools"""
    print("\nSolving TSP with OR-Tools...")
    
    # 1. Create Routing Model
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0) # 1 vehicle, starts at node 0
    routing = pywrapcp.RoutingModel(manager)

    # 2. Define Cost Function (Distance)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 3. Parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.time_limit.seconds = 30

    # 4. Solve
    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        print("No solution found!")
        return None, None

    # 5. Extract Route
    route = []
    total_distance = 0
    index = routing.Start(0)

    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route.append(node)
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        total_distance += routing.GetArcCostForVehicle(previous_index, index, 0)

    route.append(manager.IndexToNode(index)) # Add end node
    print(f"Optimal route found! Distance: {total_distance / 1000:.2f} km")
    return route, total_distance

def format_route(route, locations_df, predictions_df):
    """Format route for Firebase"""
    route_data = {
        "stops": [],
        "total_distance_km": 0,
        "total_bins": len(route) - 2,
        "created_at": int(time.time()),
    }

    total_dist = 0

    for i, node_idx in enumerate(route):
        if node_idx == 0:
            stop = {
                "order": i,
                "type": "depot",
                "bin_id": "DEPOT",
                "latitude": DEPOT_LAT,
                "longitude": DEPOT_LON,
            }
        else:
            # Bin (node_idx - 1 because bins start at index 0 in locations_df)
            bin_row = locations_df.iloc[node_idx - 1]
            bin_id = bin_row["bin_id"]
            pred_row = predictions_df[predictions_df["bin_id"] == bin_id].iloc[0]

            stop = {
                "order": i,
                "type": "bin",
                "bin_id": bin_id,
                "latitude": float(bin_row["latitude"]),
                "longitude": float(bin_row["longitude"]),
                "time_to_full_h": float(pred_row["time_to_full_h"]),
                "fill_level": float(pred_row["fill_level"]),
            }

            if i > 0:
                prev_stop = route_data["stops"][-1]
                dist = haversine_distance(
                    prev_stop["latitude"], prev_stop["longitude"],
                    stop["latitude"], stop["longitude"]
                )
                stop["distance_from_previous_km"] = round(dist, 2)
                total_dist += dist

        route_data["stops"].append(stop)

    route_data["total_distance_km"] = round(total_dist, 2)
    return route_data

def save_route_to_firebase(route_data):
    """Save to Firebase"""
    print("\nSaving route to Firebase...")
    ref = db.reference("/routes/route_1")
    ref.set(route_data)
    print("Route saved successfully!")

def main():
    try:
        start_time = time.time()
        init_firebase()

        predictions_df = fetch_predictions()
        if predictions_df.empty: return

        selected_bins = select_bins_for_collection(predictions_df)
        if selected_bins.empty: return

        locations_df = fetch_bin_locations(selected_bins["bin_id"].tolist())
        distance_matrix = create_distance_matrix(locations_df)
        
        route, _ = solve_tsp(distance_matrix)
        if route:
            route_data = format_route(route, locations_df, selected_bins)
            save_route_to_firebase(route_data)
            print(f"\n✓ Optimization done in {time.time() - start_time:.2f}s")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
