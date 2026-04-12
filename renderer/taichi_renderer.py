import taichi as ti
import numpy as np

# Initialize Taichi
ti.init(arch=ti.gpu)

# Simulation parameters
N = 1000
dt = 0.01
gravity = 9.8
damping = 0.99

# Create fields
pos = ti.Vector.field(2, dtype=ti.f32, shape=N)
vel = ti.Vector.field(2, dtype=ti.f32, shape=N)

# Initialize particles
@ti.kernel
def init():
    for i in range(N):
        pos[i] = ti.Vector([ti.random() * 0.8 + 0.1, ti.random() * 0.8 + 0.1])
        vel[i] = ti.Vector([ti.random() * 2 - 1, ti.random() * 2 - 1])

# Physics update
@ti.kernel
def update():
    for i in range(N):
        # Apply gravity
        vel[i].y -= gravity * dt
        
        # Update position
        pos[i] += vel[i] * dt
        
        # Boundary collision
        if pos[i].x < 0.05:
            pos[i].x = 0.05
            vel[i].x *= -damping
        elif pos[i].x > 0.95:
            pos[i].x = 0.95
            vel[i].x *= -damping
            
        if pos[i].y < 0.05:
            pos[i].y = 0.05
            vel[i].y *= -damping
        elif pos[i].y > 0.95:
            pos[i].y = 0.95
            vel[i].y *= -damping

# Main loop
init()
window = ti.GUI("Taichi Particle Simulation", res=(800, 800))

while window.running:
    update()
    
    # Draw particles
    window.clear(0x111111)
    window.circles(pos.to_numpy(), radius=5, color=0x00FF00)
    
    window.show()