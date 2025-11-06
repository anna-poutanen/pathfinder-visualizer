# algorithms.py
from heapq import heappush, heappop
from collections import deque
import math

# Each algorithm returns a list of steps. A step is a dict:
# { "type": "visit"|"frontier"|"path", "pos": [r,c], "extra": {...} }
# Final path steps have type "path" and present the sequence from start->goal.

def neighbors(rows, cols, r, c, allow_diagonal=False):
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    if allow_diagonal:
        dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
    for dr,dc in dirs:
        nr, nc = r+dr, c+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc

def reconstruct_path(came_from, end):
    path = []
    cur = end
    while cur in came_from:
        path.append(list(cur))
        cur = came_from[cur]
    path.append(list(cur))  # add start
    path.reverse()
    return path

def bfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    q = deque()
    q.append(tuple(start))
    visited = set([tuple(start)])
    came_from = {}
    steps = []
    steps.append({"type":"start", "pos":list(start)})
    while q:
        cur = q.popleft()
        steps.append({"type":"visit","pos":list(cur)})
        if cur == tuple(goal):
            path = reconstruct_path(came_from, cur)
            for p in path:
                steps.append({"type":"path","pos":list(p)})
            return steps
        for nr,nc in neighbors(rows, cols, cur[0], cur[1]):
            if (nr,nc) in visited: continue
            if grid[nr][nc] == 1: continue  # wall
            visited.add((nr,nc))
            came_from[(nr,nc)] = cur
            steps.append({"type":"frontier","pos":[nr,nc]})
            q.append((nr,nc))
    return steps  # no path (just exploration)

def dfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    stack = [tuple(start)]
    visited = set()
    came_from = {}
    steps = []
    steps.append({"type":"start", "pos":list(start)})
    while stack:
        cur = stack.pop()
        if cur in visited: continue
        visited.add(cur)
        steps.append({"type":"visit","pos":list(cur)})
        if cur == tuple(goal):
            path = reconstruct_path(came_from, cur)
            for p in path:
                steps.append({"type":"path","pos":list(p)})
            return steps
        for nr,nc in neighbors(rows, cols, cur[0], cur[1]):
            if (nr,nc) in visited: continue
            if grid[nr][nc] == 1: continue
            came_from[(nr,nc)] = cur
            steps.append({"type":"frontier","pos":[nr,nc]})
            stack.append((nr,nc))
    return steps

def dijkstra(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    dist = {tuple(start): 0}
    pq = []
    heappush(pq, (0, tuple(start)))
    came_from = {}
    visited = set()
    steps = []
    steps.append({"type":"start","pos":list(start)})
    while pq:
        d, cur = heappop(pq)
        if cur in visited: continue
        visited.add(cur)
        steps.append({"type":"visit","pos":list(cur), "extra":{"dist":d}})
        if cur == tuple(goal):
            path = reconstruct_path(came_from, cur)
            for p in path:
                steps.append({"type":"path","pos":list(p)})
            return steps
        for nr,nc in neighbors(rows, cols, cur[0], cur[1]):
            if grid[nr][nc] == 1: continue
            cost = grid[nr][nc] if grid[nr][nc] > 0 else 1  # treat 0 as cost 1; >1 as weighted
            nd = d + cost
            if (nr,nc) not in dist or nd < dist[(nr,nc)]:
                dist[(nr,nc)] = nd
                came_from[(nr,nc)] = cur
                heappush(pq, (nd, (nr,nc)))
                steps.append({"type":"frontier","pos":[nr,nc], "extra":{"dist":nd}})
    return steps

def manhattan(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    open_set = []
    gscore = {tuple(start): 0}
    fscore = {tuple(start): manhattan(start, goal)}
    heappush(open_set, (fscore[tuple(start)], tuple(start)))
    came_from = {}
    steps = []
    steps.append({"type":"start","pos":list(start)})
    visited = set()
    while open_set:
        f, cur = heappop(open_set)
        if cur in visited: continue
        visited.add(cur)
        steps.append({"type":"visit","pos":list(cur), "extra":{"f":f}})
        if cur == tuple(goal):
            path = reconstruct_path(came_from, cur)
            for p in path:
                steps.append({"type":"path","pos":list(p)})
            return steps
        for nr,nc in neighbors(rows, cols, cur[0], cur[1]):
            if grid[nr][nc] == 1: continue
            tentative = gscore[cur] + (grid[nr][nc] if grid[nr][nc] > 0 else 1)
            if (nr,nc) not in gscore or tentative < gscore[(nr,nc)]:
                came_from[(nr,nc)] = cur
                gscore[(nr,nc)] = tentative
                h = manhattan((nr,nc), goal)
                fscore[(nr,nc)] = tentative + h
                heappush(open_set, (fscore[(nr,nc)], (nr,nc)))
                steps.append({"type":"frontier","pos":[nr,nc], "extra":{"f":fscore[(nr,nc)], "g":tentative, "h":h}})
    return steps

def greedy_best_first(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    open_set = []
    heappush(open_set, (manhattan(start,goal), tuple(start)))
    came_from = {}
    visited = set()
    steps = []
    steps.append({"type":"start","pos":list(start)})
    while open_set:
        h, cur = heappop(open_set)
        if cur in visited: continue
        visited.add(cur)
        steps.append({"type":"visit","pos":list(cur), "extra":{"h":h}})
        if cur == tuple(goal):
            path = reconstruct_path(came_from, cur)
            for p in path:
                steps.append({"type":"path","pos":list(p)})
            return steps
        for nr,nc in neighbors(rows, cols, cur[0], cur[1]):
            if grid[nr][nc] == 1: continue
            if (nr,nc) in visited: continue
            came_from[(nr,nc)] = cur
            heappush(open_set, (manhattan((nr,nc), goal), (nr,nc)))
            steps.append({"type":"frontier","pos":[nr,nc], "extra":{"h":manhattan((nr,nc), goal)}})
    return steps
