import taichi as ti
import json
import os

# ─────────────────────────────────────────────
# Taichi initialization
# Must happen before ANY field declarations.
# arch=ti.gpu targets your RTX 4050 via CUDA.
# ─────────────────────────────────────────────
ti.init(arch=ti.gpu, debug=False, log_level=ti.INFO)

# ─────────────────────────────────────────────
# Load grid dimensions from parameters.json
# so there is ONE place to change grid size —
# the config file. Never hardcode W and H.
# ─────────────────────────────────────────────
_params_path = os.path.join(
    os.path.dirname(__file__),
    '..', 'data', 'parameters.json'
)

with open(_params_path, 'r') as f:
    _params = json.load(f)

W = int(_params['grid_width'])     # 400
H = int(_params['grid_height'])    # 600
MAX_PARTICLES = 25000

# ─────────────────────────────────────────────
# Core simulation fields
# These are allocated in GPU memory.
# simulation.py WRITES to these.
# taichi_renderer.py READS from these.
# Neither file declares these independently.
# ─────────────────────────────────────────────

# The main grid:
# 0 = empty electrolyte
# 1 = solid lithium crystal
grid = ti.field(dtype=ti.i32, shape=(W, H))

# Temperature at each cell (0.0 to 1.0 normalized)
# 0.0 = cold, 1.0 = hottest zone
temperature_field = ti.field(dtype=ti.f32, shape=(W, H))

# Particle positions — each entry is (x, y) in grid coordinates
particle_pos = ti.Vector.field(2, dtype=ti.f32, shape=MAX_PARTICLES)

# How many particles are currently alive
# .field(shape=()) means it's a single scalar, not an array
particle_count = ti.field(dtype=ti.i32, shape=())

# ─────────────────────────────────────────────
# Simulation state — renderer reads these
# for the HUD display (cycle counter, risk score)
# ─────────────────────────────────────────────
cycle_count = ti.field(dtype=ti.i32, shape=())
max_dendrite_height = ti.field(dtype=ti.i32, shape=())
risk_score = ti.field(dtype=ti.f32, shape=())

# ─────────────────────────────────────────────
# Pending write buffer — for race condition fix
# Particles write here during their step.
# At end of timestep this merges into grid.
# Prevents particles reading stale grid state.
# ─────────────────────────────────────────────
pending_grid = ti.field(dtype=ti.i32, shape=(W, H))


# ─────────────────────────────────────────────
# Utility kernel — clears pending buffer
# Called once at the start of each timestep
# ─────────────────────────────────────────────
@ti.kernel
def clear_pending():
    for x, y in pending_grid:
        pending_grid[x, y] = 0


# ─────────────────────────────────────────────
# Utility kernel — merges pending into grid
# Called once at the end of each timestep
# ─────────────────────────────────────────────
@ti.kernel
def merge_pending():
    for x, y in pending_grid:
        if pending_grid[x, y] == 1:
            grid[x, y] = 1


# ─────────────────────────────────────────────
# Verification — run this to confirm fields
# allocated correctly on GPU
# ─────────────────────────────────────────────
def verify_fields():
    print(f"Grid dimensions:     {W} x {H}")
    print(f"Grid field shape:    {grid.shape}")
    print(f"Temp field shape:    {temperature_field.shape}")
    print(f"Particle positions:  {particle_pos.shape}")
    print(f"Max particles:       {MAX_PARTICLES}")
    print(f"Pending buffer:      {pending_grid.shape}")
    print("All fields verified OK")


if __name__ == "__main__":
    verify_fields()