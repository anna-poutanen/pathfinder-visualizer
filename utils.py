# utils.py
import json

# Input: grid is a list of lists. Walls are 1, empty is 0, optional weights >1.
# Start and goal are [r,c].

def validate_payload(payload):
    if 'grid' not in payload or 'start' not in payload or 'goal' not in payload or 'algorithm' not in payload:
        return False, "Missing one of 'grid', 'start', 'goal', 'algorithm'"
    grid = payload['grid']
    start = payload['start']
    goal = payload['goal']
    rows = len(grid)
    cols = len(grid[0]) if rows>0 else 0
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return False, "Start out of bounds"
    if not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
        return False, "Goal out of bounds"
    return True, ""

