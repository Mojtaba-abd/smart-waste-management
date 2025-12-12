from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Import your existing scripts
# These must be in the same folder as api.py
import routing
import inference

app = Flask(__name__)
# Enable CORS so your Vue app (localhost:5173) can talk to this Python app (localhost:5000)
CORS(app)


@app.route("/run-optimization", methods=["POST"])
def run_optimization():
    try:
        print("🚀 Triggering Route Optimization...")
        # This calls the main() function inside routing.py
        # It will fetch data, calculate TSP, and update Firebase /routes
        routing.main()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "TSP Optimization complete. Routes updated in Firebase.",
                }
            ),
            200,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": "An internal error has occurred."}), 500


@app.route("/run-inference", methods=["POST"])
def run_inference():
    try:
        print("🧠 Triggering AI Inference...")
        # This calls the main() function inside inference.py
        # It will fetch bins, predict time-to-full, and update Firebase /predictions
        inference.main()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "AI Inference complete. Predictions updated in Firebase.",
                }
            ),
            200,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": "An internal error has occurred."}), 500


if __name__ == "__main__":
    print("🔥 Smart Waste ML Server running on http://localhost:5000")
    app.run(port=5000)
