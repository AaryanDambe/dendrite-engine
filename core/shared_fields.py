import taichi as ti

W = 400
H = 600
MAX_PARTICLES = 25000

grid = ti.Vector.field(1, dtype=ti.i32, shape=(W, H))
temperature_field = ti.field(dtype=ti.f32, shape=(W, H))
particle_pos = ti.Vector.field(2, dtype=ti.f32, shape=MAX_PARTICLES)
particle_count = ti.field(dtype=ti.i32, shape=())
cycle_count = ti.field(dtype=ti.i32, shape=())
max_dendrite_height = ti.field(dtype=ti.i32, shape=())
risk_score = ti.field(dtype=ti.f32, shape=())