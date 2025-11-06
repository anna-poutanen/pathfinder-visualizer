# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from algorithms import bfs, dfs, dijkstra, astar, greedy_best_first
from utils import validate_payload
import os

app = Flask(__name__, static_folder="static")
# Allow all origins & methods (safe for your project)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "dijkstra": dijkstra,
    "astar": astar,
    "greedy": greedy_best_first
}

# Serve your frontend (optional, if you want Railway to serve it)
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

# Updated API endpoint to handle both POST and OPTIONS
@app.route("/solve", methods=["POST", "OPTIONS"])
def solve():
    if request.method == "OPTIONS":
        # Handles preflight requests
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    payload = request.get_json()
    ok, msg = validate_payload(payload)
    if not ok:
        return jsonify({"error": msg}), 400

    grid = payload['grid']
    start = payload['start']
    goal = payload['goal']
    alg_name = payload['algorithm'].lower()
    allow_diag = payload.get("allow_diagonal", False)

    if alg_name not in ALGORITHMS:
        return jsonify({"error": "Unknown algorithm"}), 400

    steps = ALGORITHMS[alg_name](grid, start, goal)
    return jsonify({"steps": steps})

if __name__ == "__main__":
    # host='0.0.0.0' is required for Railway
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
