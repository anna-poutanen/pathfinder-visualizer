# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from algorithms import bfs, dfs, dijkstra, astar, greedy_best_first
from utils import validate_payload
import os

app = Flask(__name__, static_folder="static")  # <-- set static folder
CORS(app)

ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "dijkstra": dijkstra,
    "astar": astar,
    "greedy": greedy_best_first
}

# Serve your frontend
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

# API endpoint for solving
@app.route("/solve", methods=["POST"])
def solve():
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
        return jsonify({"error":"Unknown algorithm"}), 400
    steps = ALGORITHMS[alg_name](grid, start, goal)
    return jsonify({"steps": steps})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
