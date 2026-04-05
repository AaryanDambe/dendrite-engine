# dendrite-engine
A Python physics engine simulating dendritic crystal growth and Diffusion-Limited Aggregation (DLA) for electrochemical applications, Coded for a First year Project Based Learning Engineering Chemistry Project.

---

## What This Is

This project is a computational physics engine that simulates **dendrite growth** inside lithium-ion battery cells which are the primary physical mechanism responsible for battery degradation and, in extreme cases, thermal runaway (fire) in electric vehicles.

It is not a toy visualizer. The underlying algorithm (Diffusion-Limited Aggregation) is the same class of model used in real materials science research. The simplifications we made are deliberate, documented, and scientifically justified. The goal is a **working, calibrated, parallelized simulation** that produces physically meaningful outputs for a specific real-world use case: predicting how fast-charging vs slow-charging degrades a lithium-ion cell over its lifetime.

---

## The Problem We Are Solving

During charging, lithium ions travel from the cathode, through the liquid electrolyte, and deposit onto the graphite anode. Under ideal conditions this is smooth and uniform. Under stress — fast charging, elevated temperature, aged electrolyte — the deposition becomes uneven and lithium begins forming **dendrites**: needle-like crystal structures that grow upward from the anode surface toward the cathode.

Two failure modes result:
1. **Capacity fade** — dendrites trap lithium in unusable crystal structures, reducing the amount available for future cycles
2. **Short circuit** — if a dendrite bridges the full anode-to-cathode gap, it creates a direct electrical short, leading to rapid heat generation and potential thermal runaway

This simulation models the electrolyte gap where this process occurs, predicts dendrite growth trajectory under different operating conditions, and outputs actionable risk metrics.

---

## What We Are Actually Simulating

We simulate a **2D cross-section of the liquid electrolyte gap** in a lithium-ion cell, viewed from the side.

```
TOP:    ─────────────────────────────────────────
        [ ion source boundary — cathode side    ]
        [                                        ]
        [        electrolyte space              ]
        [     (this is our simulation grid)     ]
        [                                        ]
        [ dendrite growth zone                  ]
BOTTOM: ─────────────────────────────────────────
        [ graphite anode surface — seed row     ]
```

We are **not** simulating:
- The interior chemistry of the cathode or anode bulk
- SEI (solid electrolyte interphase) layer formation
- Mechanical stress and anode expansion
- 3D volumetric structure
- Full Nernst-Planck ion transport equations

Each of these omissions is intentional and documented in the limitations section below. The cathode is treated as a boundary condition, an ion source whose rate is set by the charge current, derived from real manufacturer datasheets via Faraday's Law.

This is a lithium-ion simulation with **liquid electrolyte**. It is not a solid-state battery simulation. All calibration data targets commercially available 2170-format cells.

---

## The Algorithm — How It Works

### Core: Diffusion-Limited Aggregation (DLA)

The simulation grid is a 2D array of cells. Each cell is either:
- `0` — liquid electrolyte (empty)
- `1` — solid lithium crystal (deposited)

The bottom row is pre-seeded as all `1`s — this represents the existing anode surface.

A lithium ion is modeled as a **random-walking particle**:
1. Spawn at a random position near the top of the grid
2. Each timestep: move randomly to one of 4 adjacent cells (Brownian motion)
3. If the particle's current position is adjacent to any existing solid cell, it has a probability `α` (alpha) of depositing (becoming a new solid cell)
4. If it deposits: freeze it, spawn the next particle
5. If it walks off the boundary: kill it, spawn the next particle

Repeat this for thousands of particles across hundreds of simulated cycles. The branching fractal structure that emerges is not programmed, rather it arises from geometry. Tips of existing crystal intercept more random walkers than valleys, so tips grow faster. This produces the needle-like morphology seen in real SEM images.

### Phase 1 — Pure DLA
Random walk with sticking probability = 1.0. Proof of concept. Establishes the fractal structure.

### Phase 2 — Sticking Probability
Introduce `α ∈ [0,1]`. When a particle is adjacent to a solid cell, it deposits only if `random() < α`. This models electrolyte health and overpotential:
- High α → aggressive deposition, sharp dangerous dendrites → models fast charging or degraded electrolyte
- Low α → slow uniform deposition → models slow charging or fresh battery

The value of α for specific operating conditions is derived from Butler-Volmer kinetics by the research team. In the simulation it is used as a pre-computed scalar per operating condition, not evaluated cell-by-cell (see Limitations).

### Phase 3 — Temperature Gradient
A 2D temperature field is overlaid on the grid. Diffusion rate at each cell is scaled by the Arrhenius equation:

```
diffusion_rate(x,y) = D₀ × exp(-Eₐ / R × T(x,y))
```

Where:
- `D₀` = pre-exponential diffusion factor (from literature, specific to electrolyte)
- `Eₐ` = activation energy for Li⁺ diffusion (from literature)
- `R` = gas constant (8.314 J/mol·K)
- `T(x,y)` = local temperature in Kelvin

Hotter regions diffuse faster, particles take more steps per timestep. This models uneven internal heating, which develops as a battery ages, causing spatially non-uniform dendrite growth. The temperature field is configurable and can approximate real thermal profiles from published measurements.

---

## Inputs and Outputs

### Inputs

| Parameter | Physical Meaning | Source |
|---|---|---|
| `alpha` | Sticking probability — electrolyte/overpotential state | Research team (Butler-Volmer) |
| `charge_rate` | Particle injection rate — maps to real current density via Faraday's Law | Research team (manufacturer datasheet) |
| `temperature_gradient` | Spatial heat distribution bias | Research team (published thermal maps) |
| `battery_age_preset` | Combination config: Fresh / Slightly Used / Moderately Used / Heavily Degraded | Calibrated parameter bundle |
| `num_cycles` | How many charge events to simulate | User-defined |
| `ensemble_runs` | Number of repeated runs to average (removes stochastic noise) | Default: 50 |

### Outputs

| Output | What It Means | Who Uses It |
|---|---|---|
| Live dendrite visualization | Real-time view of crystal growth during simulation | Visual demonstration |
| Max dendrite height per cycle | Growth trajectory curve — the primary time-series result | All analysis |
| Short-circuit risk score | `(max_height / grid_height) × 100` — single actionable number | BMS lookup table, warranty modeling |
| Ensemble mean height profile | Averaged spatial distribution across anode width (50 runs) | Identifying hotspot zones |
| Fast vs slow charge comparison | Side-by-side growth curves under different charge rate conditions | Engineering decision support |

### The Core Scientific Result

The simulation answers one question with statistical rigor:

> *Under equivalent initial conditions, how many more safe charge cycles does slow charging provide compared to fast charging, and where on the anode does degradation concentrate?*

The absolute cycle numbers carry calibration uncertainty. The **ratio** between fast and slow charge cycle life is robust, calibration error cancels in the comparison. This ratio is the defensible scientific output.

---

## Real-World Calibration

For the simulation to produce physically grounded predictions (not just qualitative comparisons), the following parameters must be sourced from published literature for a specific target cell. Our research team is responsible for finding these.

| Parameter | Symbol | Unit | Status |
|---|---|---|---|
| Li⁺ diffusion coefficient in target electrolyte | D₀ | m²/s | ⬜ Pending |
| Activation energy for Li⁺ diffusion | Eₐ | J/mol | ⬜ Pending |
| Anode surface dimensions of target cell | — | mm × mm | ⬜ Pending |
| Rated fast-charge current density | I_fast | A/m² | ⬜ Pending |
| Rated slow-charge current density | I_slow | A/m² | ⬜ Pending |
| Cycle life rating to 80% capacity | N_rated | cycles | ⬜ Pending |
| Operating temperature range | T_min, T_max | K | ⬜ Pending |

**Target cell:** recommended: LG M50 2170 (used in Tesla Model 3, well-documented in public literature)

Once these are filled in, one simulation cycle maps to one real charge event via:

```
particles_per_cycle = (I × A_cell × t_charge) / (n × F × A_grid_cell)
```

Where `I` is current density, `A_cell` is anode area, `t_charge` is charge duration, `n=1` for lithium, `F` is Faraday's constant, and `A_grid_cell` is the real area represented by one grid cell.

---

## Architecture

```
parameters.json          ← single source of truth for all inputs
      │
      ▼
simulation.py            ← core DLA engine (Python + Numba/Taichi)
      │
      ├──────────────────────────────────────────┐
      ▼                                          ▼
taichi_renderer.py               simulation_output.csv
(live GPU visualization          (per-cycle statistics,
 reads Taichi field directly)     ensemble results)
                                         │
                                         ▼
                                 analytics_dashboard.py
                                 (Matplotlib charts:
                                  growth curves,
                                  risk scores,
                                  spatial profiles)
```

The simulation and the dashboard are **decoupled through files**. The dashboard reads CSVs. It does not import the simulation. This means the UI can be built and tested against mock data independently, and swapped to real output on integration day with zero code changes.

### Parallelization

The particle walk loop is parallelized using **Taichi** (GPU acceleration via the RTX 4050). Each particle's random walk is independent, so N particles can be stepped simultaneously across GPU cores. A stale-read buffer (pending write array merged once per timestep) prevents race conditions without meaningful performance cost.

Grid resolution target: **400×600 cells**, 20,000–30,000 particles per cycle, running on GPU. Expected throughput: 2–4 seconds per simulated cycle.

---

## Team Structure

| Role | Person | Owns | Does NOT touch |
|---|---|---|---|
| Tech Lead / Architect | — | `core/simulation.py`, repo setup, Notion, LaTeX formatting | Renderer internals |
| Co-Coder | — | `renderer/taichi_renderer.py`, Taichi GGUI | Simulation physics logic |
| UI / Visuals | — | `ui/control_panel.py`, `ui/analytics_dashboard.py` | Taichi, simulation core |
| Scientific Validator 1 | — | Parameter sheet, literature sourcing, calibration | Code |
| Scientific Validator 2 | — | Output comparison to real-world reference data, report analysis sections | Code |
| PPT / Executive Summary | — | Slide deck, 2-page summary, use case framing | Code |

### The Decoupling Contract

On Day 1, the Tech Lead generates `data/mock_output.csv` — a synthetic dataset in the exact format the real simulation will produce. The UI person builds everything against this file. On integration day, `mock_output.csv` is replaced with real simulation output. The UI code does not change.

**Mock data contract — `simulation_output.csv` schema:**
```
cycle, fast_charge_height, slow_charge_height, risk_score_fast, risk_score_slow
1, 3.2, 1.1, 3.5, 1.2
2, 5.8, 1.9, 6.4, 2.0
...
```

---

## Limitations — What This Simulation Cannot Do

These are not oversights. They are deliberate scope decisions made for a one-week first-year project. Each is documented here so future readers understand what the model assumes away.

**1. No SEI layer formation**
The solid electrolyte interphase is a thin passivation layer that forms from electrolyte decomposition. Modeling it requires 6-12 coupled electrochemical reactions running simultaneously with dendrite growth. It is a second complete simulation engine. Out of scope.

**2. No mechanical stress modeling**
Lithium deposition causes the anode to expand (up to 10% per cycle for graphite). Stress-driven cracking changes deposition geometry over time. Modeling this requires Finite Element Analysis which is an entirely different mathematical framework. Out of scope for this project.

**3. 2D cross-section only, not 3D**
Real dendrites are volumetric coral-like structures. A 3D simulation requires 200× more memory, a different renderer, and different analysis methods. The 2D cross-section captures the growth dynamics and spatial distribution correctly; it cannot capture out-of-plane branching. The visual and quantitative behavior of 2D DLA matches published 2D cross-section SEM images well.

**4. Spatially uniform alpha**
Alpha (sticking probability) is computed from Butler-Volmer kinetics for a given operating condition and applied uniformly across the grid. In reality, local overpotential varies cell-by-cell and requires solving Poisson's equation for the electric field at every timestep. The uniform approximation is physically justified as a spatial average and is standard in DLA-based battery models at this level of fidelity.

**5. No absolute time calibration guarantee**
Cycle-to-real-time mapping depends on the diffusion coefficient calibration from literature. If that coefficient carries uncertainty (which it does — it varies with temperature, electrolyte concentration, and cell aging), the absolute time predictions scale proportionally. The relative comparison between scenarios (fast vs slow charge) is robust. Absolute lifetime predictions should be treated as order-of-magnitude estimates, not engineering specifications.

**6. Not a solid-state battery simulation**
DLA models diffusion through a liquid medium. Dendrite propagation in solid-state electrolytes is driven by crack mechanics in a rigid lattice. This simulation is valid for liquid and gel electrolyte lithium-ion cells only.

---

## Getting Started

### Prerequisites
```bash
pip install numpy numba taichi matplotlib pandas scipy
```

### Run the simulation
```bash
python main.py
```

### Configuration
Edit `data/parameters.json` to change operating conditions, or use the UI control panel.

### Run with mock data only (UI development)
```bash
python ui/analytics_dashboard.py --mock
```

---

## Repository Structure

```
dendrite-engine/
├── core/
│   └── simulation.py          # DLA engine, particle logic, ensemble runner
├── renderer/
│   └── taichi_renderer.py     # GPU-accelerated live visualization
├── ui/
│   ├── control_panel.py       # Parameter sliders and presets
│   └── analytics_dashboard.py # Post-simulation charts and export
├── data/
│   ├── parameters.json        # Active simulation config
│   ├── mock_output.csv        # Synthetic data for UI development
│   └── simulation_output.csv  # Written by simulation after each run
├── research/
│   └── parameter_sheet.md     # Physical constants — research team fills this
├── report/
│   └── findings.md            # Plain-text findings for LaTeX conversion
└── main.py                    # Entry point — wires all components together
```

---

## Academic Context

This project was built as part of a first-year engineering chemistry curriculum. The scientific framing, parameter calibration methodology, and output interpretation were developed in consultation with published electrochemistry literature. The DLA algorithm for electrodeposition modeling has precedent in peer-reviewed materials science research.

The simulation is an approximation. It is presented as one, documented as one, and should be evaluated as a physically motivated, parameterized model that produces comparative predictions with clearly bounded uncertainty, not a replacement for experimental characterization.

