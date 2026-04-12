import taichi as ti
import random

ti.init(arch=ti.cpu)  # change to ti.gpu if supported

# Grid size
N = 200

# Fields
grid = ti.field(dtype=ti.i32, shape=(N, N))  # 0 empty, 1 occupied

# Particle properties
max_particles = 2000
positions = ti.Vector.field(2, dtype=ti.i32, shape=max_particles)
active = ti.field(dtype=ti.i32, shape=max_particles)

# Parameters
stick_prob = 0.5
E_strength = 3  # electric field bias (increase for fast charging)

# Initialize electrode (bottom row)
@ti.kernel
def init():
    for i, j in grid:
        grid[i, j] = 0

    for i in range(N):
        grid[i, 0] = 1  # seed dendrite at bottom


# Spawn particles at top
def spawn_particles():
    for i in range(max_particles):
        if active[i] == 0:
            positions[i] = ti.Vector([random.randint(0, N - 1), N - 1])
            active[i] = 1


# Check if near cluster
@ti.func
def near_cluster(x, y):
    found = 0

    for dx, dy in ti.static([(1,0), (-1,0), (0,1), (0,-1)]):
        nx = x + dx
        ny = y + dy

        if 0 <= nx < N and 0 <= ny < N:
            if grid[nx, ny] == 1:
                found = 1  # ✅ set flag instead of returning

    return found


# Simulation step
@ti.kernel
def step():
    for i in range(max_particles):
        if active[i] == 1:
            pos = positions[i]

            # Random walk
            dx = ti.random(ti.i32) % 3 - 1
            dy = ti.random(ti.i32) % 3 - 1

            # Electric field bias (downward)
            dy -= E_strength

            new_x = min(max(pos[0] + dx, 0), N - 1)
            new_y = min(max(pos[1] + dy, 0), N - 1)

            # Stick condition
            if near_cluster(new_x, new_y) == 1:
                if ti.random() < stick_prob:
                    grid[new_x, new_y] = 1
                    active[i] = 0
                    continue

            positions[i] = ti.Vector([new_x, new_y])


# Simple visualization
gui = ti.GUI("DLA Dendrite Growth", (N, N))

init()
spawn_particles()

while gui.running:
    for _ in range(5):  # multiple steps per frame
        step()

    # Draw grid
    img = grid.to_numpy().astype('float32')* 1.0
    gui.set_image(img)
    gui.show()
