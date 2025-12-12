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

# Depot location (example - replace with your actual depot coordinates)
DEPOT_LAT = 33.5731
DEPOT_LON = 44.3668

# Threshold for urgent collection (hours)
TIME_THRESHOLD = 12

# Maximum number of bins to visit in one route
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
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers
    r = 6371

    return c * r


def fetch_predictions():
    """Fetch all predictions from Firebase"""
    print("Fetching predictions from Firebase...")
    ref = db.reference("/predictions")
    predictions = ref.get()

    if not predictions:
        print("No predictions found")
        return pd.DataFrame()

    # Convert to DataFrame
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
            locations.append(
                {
                    "bin_id": bin_id,
                    "latitude": bin_data.get("latitude", 0),
                    "longitude": bin_data.get("longitude", 0),
                }
            )

    return pd.DataFrame(locations)


def select_bins_for_collection(
    predictions_df, threshold=TIME_THRESHOLD, max_bins=MAX_BINS_PER_ROUTE
):
    """
    Select bins that need collection based on time_to_full prediction.
    Prioritizes most urgent bins.
    """
    print(f"\nSelecting bins with time_to_full <= {threshold} hours...")

    # Filter bins that need collection soon
    urgent_bins = predictions_df[predictions_df["time_to_full_h"] <= threshold].copy()

    if len(urgent_bins) == 0:
        # If no urgent bins, select top N bins with shortest time to full
        print(
            f"No urgent bins found. Selecting {max_bins} bins with shortest time to full..."
        )
        urgent_bins = predictions_df.nsmallest(max_bins, "time_to_full_h").copy()
    elif len(urgent_bins) > max_bins:
        # If too many urgent bins, select the most urgent ones
        print(
            f"Found {len(urgent_bins)} urgent bins. Selecting {max_bins} most urgent..."
        )
        urgent_bins = urgent_bins.nsmallest(max_bins, "time_to_full_h")

    # Sort by urgency
    urgent_bins = urgent_bins.sort_values("time_to_full_h")

    print(f"Selected {len(urgent_bins)} bins for collection")
    print("\nSelected bins:")
    print(
        urgent_bins[["bin_id", "time_to_full_h", "fill_level"]].to_string(index=False)
    )

    return urgent_bins


def create_distance_matrix(locations_df):
    """
    Create distance matrix using Haversine formula.
    First location is depot, remaining are bins.
    Returns distance matrix in meters.
    """
    print("\nCreating distance matrix...")

    # Prepare coordinates: depot first, then bins
    coords = [(DEPOT_LAT, DEPOT_LON)]
    for idx, row in locations_df.iterrows():
        coords.append((row["latitude"], row["longitude"]))

    n = len(coords)
    distance_matrix = np.zeros((n, n))

    # Calculate distances between all pairs
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lon1 = coords[i]
                lat2, lon2 = coords[j]
                # Convert km to meters
                distance_matrix[i][j] = (
                    haversine_distance(lat1, lon1, lat2, lon2) * 1000
                )

    print(f"Distance matrix created: {n}x{n} locations")

    return distance_matrix.astype(int)


def create_data_model(distance_matrix, num_bins):
    """Create data model for OR-Tools solver"""
    data = {}
    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = 1
    data["depot"] = 0  # Depot is first location
    return data


def solve_tsp(distance_matrix):
    """
    Solve TSP using Google OR-Tools.
    Returns the optimal route as list of indices.
    """
    print("\nSolving TSP with OR-Tools...")

    # Create data model
    data = create_data_model(distance_matrix, len(distance_matrix) - 1)

    # Create routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create routing model
    routing = pywrapcp.RoutingModel(manager)

    # Create distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 30

    # Solve
    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        print("No solution found!")
        return None, None

    # Extract route
    route = []
    total_distance = 0
    index = routing.Start(0)

    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route.append(node)
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        total_distance += routing.GetArcCostForVehicle(previous_index, index, 0)

    # Add final node (return to depot)
    route.append(manager.IndexToNode(index))

    print(f"Optimal route found!")
    print(f"Total distance: {total_distance / 1000:.2f} km")

    return route, total_distance


def format_route(route, locations_df, predictions_df):
    """
    Format route into readable structure for Firebase.
    Route indices: 0 = depot, 1+ = bin indices
    """
    route_data = {
        "stops": [],
        "total_distance_km": 0,
        "total_bins": len(route) - 2,  # Exclude depot at start and end
        "created_at": int(time.time()),
    }

    total_distance = 0

    for i, node_idx in enumerate(route):
        if node_idx == 0:
            # Depot
            stop = {
                "order": i,
                "type": "depot",
                "latitude": DEPOT_LAT,
                "longitude": DEPOT_LON,
            }
        else:
            # Bin (node_idx - 1 because depot is at index 0)
            bin_row = locations_df.iloc[node_idx - 1]
            bin_id = bin_row["bin_id"]

            # Get prediction data
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

            # Calculate distance from previous stop
            if i > 0:
                prev_stop = route_data["stops"][-1]
                distance_km = haversine_distance(
                    prev_stop["latitude"],
                    prev_stop["longitude"],
                    stop["latitude"],
                    stop["longitude"],
                )
                stop["distance_from_previous_km"] = round(distance_km, 2)
                total_distance += distance_km

        route_data["stops"].append(stop)

    route_data["total_distance_km"] = round(total_distance, 2)

    return route_data


def save_route_to_firebase(route_data, route_id="route_1"):
    """Save optimized route to Firebase"""
    print(f"\nSaving route to Firebase at /routes/{route_id}...")

    ref = db.reference(f"/routes/{route_id}")
    ref.set(route_data)

    print(f"Route saved successfully!")
    print(f"\nRoute Summary:")
    print(f"  Total bins to collect: {route_data['total_bins']}")
    print(f"  Total distance: {route_data['total_distance_km']:.2f} km")
    print(f"  Number of stops: {len(route_data['stops'])}")


def print_route_details(route_data):
    """Print detailed route information"""
    print("\n=== OPTIMIZED COLLECTION ROUTE ===\n")

    for stop in route_data["stops"]:
        if stop["type"] == "depot":
            print(f"Stop {stop['order']}: DEPOT")
            print(f"  Location: ({stop['latitude']:.4f}, {stop['longitude']:.4f})")
        else:
            print(f"Stop {stop['order']}: Bin {stop['bin_id']}")
            print(f"  Location: ({stop['latitude']:.4f}, {stop['longitude']:.4f})")
            print(f"  Fill Level: {stop['fill_level']:.1f}%")
            print(f"  Time to Full: {stop['time_to_full_h']:.1f} hours")
            if "distance_from_previous_km" in stop:
                print(
                    f"  Distance from previous: {stop['distance_from_previous_km']:.2f} km"
                )
        print()


def main():
    """Main routing optimization pipeline"""
    try:
        start_time = time.time()

        # Initialize Firebase
        init_firebase()

        # Fetch predictions
        predictions_df = fetch_predictions()

        if predictions_df.empty:
            print("No predictions available. Run inference.py first.")
            return

        # Select bins for collection
        selected_bins = select_bins_for_collection(predictions_df)

        if selected_bins.empty:
            print("No bins selected for collection")
            return

        # Fetch bin locations
        bin_ids = selected_bins["bin_id"].tolist()
        locations_df = fetch_bin_locations(bin_ids)

        # Create distance matrix
        distance_matrix = create_distance_matrix(locations_df)

        # Solve TSP
        route, total_distance = solve_tsp(distance_matrix)

        if route is None:
            print("Failed to find optimal route")
            return

        # Format route
        route_data = format_route(route, locations_df, selected_bins)

        # Print route details
        print_route_details(route_data)

        # Save to Firebase
        save_route_to_firebase(route_data)

        elapsed = time.time() - start_time
        print(f"\n✓ Route optimization completed in {elapsed:.2f} seconds")

    except Exception as e:
        print(f"Error during route optimization: {e}")
        raise


if __name__ == "__main__":
    main()
