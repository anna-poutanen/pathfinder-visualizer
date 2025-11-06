// ---------------------- ELEMENTS ----------------------
const canvas = document.getElementById('grid');
const ctx = canvas.getContext('2d');
const algorithmSelect = document.getElementById('algorithm');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const stepBtn = document.getElementById('stepBtn');
const resetBtn = document.getElementById('resetBtn');
const randomWallsBtn = document.getElementById('randomWallsBtn');
const speedInput = document.getElementById('speed');
const speedValueDisplay = document.getElementById('speedValue');
const status = document.getElementById('status');

const algorithmInfo = {
  bfs: {
    name: "Breadth-First Search (BFS)",
    description: "Explores all neighbors level by level. Guarantees shortest path in unweighted grids.",
    complexity: "O(V + E)"
  },
  dfs: {
    name: "Depth-First Search (DFS)",
    description: "Explores as deep as possible before backtracking. Not guaranteed shortest path.",
    complexity: "O(V + E)"
  },
  dijkstra: {
    name: "Dijkstra's Algorithm",
    description: "Uses a priority queue to expand lowest-cost nodes. Guarantees shortest path.",
    complexity: "O((V + E) log V)"
  },
  astar: {
    name: "A* Algorithm",
    description: "Uses a heuristic to prioritize nodes closer to goal. Efficient and finds shortest path.",
    complexity: "O(E)"
  },
  greedy: {
    name: "Greedy Best-First Search",
    description: "Prioritizes nodes closest to goal. Very fast, but not guaranteed shortest path.",
    complexity: "O(E)"
  }
};

// ---------------------- VARIABLES ----------------------
let ROWS = 25;
let COLS = 25;
let CELL = 20; // initial size, will be recalculated
let grid = [];
let start = [2, 2];
let goal = [22, 22];
let dragging = null;
let steps = [];
let stepIndex = 0;
let playing = false;
let timer = null;

// ---------------------- FUNCTIONS ----------------------
function initGrid() {
  grid = Array.from({ length: ROWS }, () => Array.from({ length: COLS }, () => 0));
  start = [2, 2];
  goal = [ROWS - 3, COLS - 3];
  steps = [];
  stepIndex = 0;
  playing = false;
  clearTimer();
  draw();
}

function clearTimer() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function resizeCanvas() {
  const maxHeight = window.innerHeight * 0.6;
  const maxWidth = window.innerWidth * 0.8;
  const size = Math.min(maxHeight, maxWidth);
  canvas.width = size;
  canvas.height = size;
  CELL = canvas.width / COLS;
  draw();
}

function randomWalls(prob = 0.25) {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if ((r === start[0] && c === start[1]) || (r === goal[0] && c === goal[1])) continue;
      grid[r][c] = Math.random() < prob ? 1 : 0;
    }
  }
  draw();
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // draw cells
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const x = c * CELL;
      const y = r * CELL;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(x, y, CELL, CELL);

      if (grid[r][c] === 1) {
        ctx.fillStyle = '#888888';
        ctx.fillRect(x + 1, y + 1, CELL - 2, CELL - 2);
      }

      ctx.strokeStyle = '#cccccc';
      ctx.strokeRect(x, y, CELL, CELL);
    }
  }

  // draw steps
  for (let i = 0; i < stepIndex && i < steps.length; i++) {
    const s = steps[i];
    if (!s || !s.pos) continue;
    const [r, c] = s.pos;
    const x = c * CELL;
    const y = r * CELL;

    if (s.type === 'frontier') ctx.fillStyle = '#a0d468';
    else if (s.type === 'visit') ctx.fillStyle = '#4caf50';
    else if (s.type === 'path') ctx.fillStyle = '#9b59b6';

    ctx.fillRect(x + 1, y + 1, CELL - 2, CELL - 2);
  }

  // start & goal
  ctx.fillStyle = '#5ab4f8';
  ctx.fillRect(start[1] * CELL + 1, start[0] * CELL + 1, CELL - 2, CELL - 2);
  ctx.fillStyle = '#f5a623';
  ctx.fillRect(goal[1] * CELL + 1, goal[0] * CELL + 1, CELL - 2, CELL - 2);
}

// ---------------------- MOUSE INTERACTIONS ----------------------
canvas.addEventListener('mousedown', (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const c = Math.floor(x / CELL);
  const r = Math.floor(y / CELL);
  if (r === start[0] && c === start[1]) dragging = 'start';
  else if (r === goal[0] && c === goal[1]) dragging = 'goal';
  else {
    grid[r][c] = grid[r][c] ? 0 : 1;
    draw();
  }
});
canvas.addEventListener('mousemove', (e) => {
  if (!dragging) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const c = Math.floor(x / CELL);
  const r = Math.floor(y / CELL);
  if (r < 0 || c < 0 || r >= ROWS || c >= COLS) return;
  if (dragging === 'start') start = [r, c];
  if (dragging === 'goal') goal = [r, c];
  draw();
});
canvas.addEventListener('mouseup', () => (dragging = null));
canvas.addEventListener('mouseleave', () => (dragging = null));

// ---------------------- FETCH STEPS ----------------------
async function fetchSteps() {
  status.innerText = 'Computing...';
  const payload = { grid, start, goal, algorithm: algorithmSelect.value };
  try {
    const res = await fetch('https://pathfinder-visualizer-production.up.railway.app/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const txt = await res.text();
      status.innerText = 'Server error: ' + txt;
      return;
    }
    const data = await res.json();
    steps = data.steps || [];
    stepIndex = 0;
    status.innerText = `Got ${steps.length} steps.`;
    draw();
  } catch (err) {
    status.innerText = 'Fetch error: ' + err.message;
  }
}

// ---------------------- PLAYBACK ----------------------
function play() {
  if (playing) return;
  playing = true;

  const sliderValue = parseInt(speedInput.value);
  const interval = Math.max(1, 200 - sliderValue * 2);

  clearTimer();
  timer = setInterval(() => {
    if (stepIndex < steps.length) {
      stepIndex++;
      draw();
    } else {
      clearTimer();
      playing = false;
      status.innerText = 'Finished';
    }
  }, interval);
}

function pause() {
  playing = false;
  clearTimer();
}

function stepOnce() {
  if (stepIndex < steps.length) stepIndex++;
  draw();
}

// ---------------------- BUTTONS ----------------------
startBtn.onclick = async () => {
  await fetchSteps();
  play();
};
pauseBtn.onclick = () => pause();
stepBtn.onclick = async () => {
  if (steps.length === 0) await fetchSteps();
  stepOnce();
};
resetBtn.onclick = () => {
  initGrid();
  status.innerText = 'Reset';
};
randomWallsBtn.onclick = () => {
  randomWalls(0.28);
  status.innerText = 'Random walls generated';
};

// ---------------------- SPEED DISPLAY ----------------------
speedInput.addEventListener('input', () => {
  const value = parseInt(speedInput.value);
  speedValueDisplay.innerText = value;
  if (value > 80) status.innerText = 'Speed: Very Fast';
  else if (value > 40) status.innerText = 'Speed: Medium';
  else status.innerText = 'Speed: Slow';
});

// ---------------------- ALGORITHM INFO ----------------------
algorithmSelect.addEventListener('change', () => {
  const alg = algorithmSelect.value;
  const info = algorithmInfo[alg];
  const infoDiv = document.getElementById('algorithmInfo');
  if (info) {
    infoDiv.innerHTML = `<strong>${info.name}</strong><br>${info.description}<br><em>Complexity: ${info.complexity}</em>`;
  } else {
    infoDiv.innerHTML = "";
  }
});

// ---------------------- START ----------------------
initGrid();
resizeCanvas();
algorithmSelect.dispatchEvent(new Event('change'));
window.addEventListener('resize', resizeCanvas);
