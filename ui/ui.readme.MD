# UI & Visuals — Developer Brief
## Dendrite Physics Engine

**Your file:** `ui/control_panel.py` and `ui/analytics_dashboard.py`
**Your data source:** `data/mock_output.csv` and `data/mock_spatial.csv`
**Your config source:** `data/parameters.json`
**Do NOT touch:** `core/`, `renderer/`, `main.py`

You are building two things: a parameter control panel and a post-simulation
analytics dashboard. The live dendrite animation is owned by the renderer
developer — that is not your responsibility. Your job is everything the user
interacts with before the simulation runs, and everything they see after it
finishes.

---

## What the Simulation Actually Models — Read This First

Before building any UI you need to understand what the simulation computes.
Every slider, every chart, and every output metric maps to one of these.

| Factor | What It Means Physically | Where It Appears in UI |
|---|---|---|
| Ion diffusion rate | How fast Li⁺ ions move through electrolyte | Implicit in charge rate slider |
| Temperature gradient | Heat concentrates in battery center, drives faster growth there | Temperature gradient slider + Chart 3 hotspot |
| Sticking probability α | Derived from ΔG_act formula — how likely an ion deposits on contact | Alpha slider |
| Surface curvature effect | Sharp dendrite tips grow faster due to Gibbs-Thomson effect | Visible in live renderer — no direct slider |
| Electric potential field | Laplace-solved field drives ions toward anode | Implicit — affects growth rate automatically |
| Ion concentration depletion | Fast growth empties local ion supply, causes branching | Concentration field chart (Chart 6) |
| Separator resistance | Ions slow down near cathode-side boundary | Separator factor slider |
| Nucleation heterogeneity | Dendrites start at random defect sites on anode | Seed roughness slider |
| Electrolyte degradation | Alpha increases each cycle as electrolyte breaks down | Degradation rate slider |
| Charge rate | Maps to real current density via Faraday's Law | Charge rate slider + Fast/Slow toggle |
| Battery age preset | Loads a calibrated bundle of all parameters | Preset buttons |
| Edge current enhancement | More ions arrive at anode edges due to geometry | Edge factor slider |
| SEI layer growth | Parabolic growth consumes lithium and increases resistance | SEI chart (Chart 7) |
| Sand's Time | Predicts when branching becomes inevitable | HUD indicator + Chart 8 |

---

## Aesthetic Direction

**Dark. Premium. Ambient.**

- Background: near-black `#0a0a12` or `#080810`
- Accent: electric blue `#4FC3F7` for active elements, highlights, borders
- Secondary accent: amber `#FFB300` for warnings
- Danger: `#FF4444` for critical risk, short-circuit threshold crossings
- Success: `#4ADE80` for safe states
- SEI indicator color: golden `#FFD700`
- Sand's Time indicator: cyan `#00E5FF` before threshold, red `#FF3333` after
- All panels: dark surface `#12121e` with `1px` border `#1e1e3a`
- Typography: monospace for all numbers. `Consolas` or `Courier New`.
  No Arial or sans-serif on data readouts.
- Gradients on chart fills, backgrounds, button hover states.
- No white backgrounds anywhere.

Reference aesthetic: Bloomberg terminal crossed with a high-end scientific
instrument. Every number feels like it means something.

---

## Window 1 — Control Panel (`ui/control_panel.py`)

Standalone Python window in Tkinter or PyQt5.
Launches before simulation starts.
Writes to `data/parameters.json` on Run.
Does NOT import anything from `core/` or `renderer/`.

---

### Section 1 — Battery Age Preset Selector

Four large buttons at the top, horizontally arranged.

```
[ FRESH ]  [ SLIGHTLY USED ]  [ MODERATELY USED ]  [ HEAVILY DEGRADED ]
```

Active preset glows with accent border `#4FC3F7`.
Clicking loads the full parameter bundle into ALL sliders simultaneously.

| Preset | alpha | charge_rate | temp_gradient | degradation_rate | sep_factor | edge_factor | seed_roughness | sei_growth_rate |
|---|---|---|---|---|---|---|---|---|
| Fresh | 0.15 | 3 | 0.20 | 0.001 | 0.85 | 1.10 | 0.05 | 0.001 |
| Slightly used | 0.30 | 5 | 0.40 | 0.002 | 0.70 | 1.20 | 0.15 | 0.002 |
| Moderately used | 0.50 | 8 | 0.65 | 0.003 | 0.55 | 1.30 | 0.30 | 0.003 |
| Heavily degraded | 0.75 | 12 | 0.85 | 0.005 | 0.35 | 1.40 | 0.55 | 0.005 |

---

### Section 2 — Parameter Sliders

Ten sliders total. All visible simultaneously — no tabs, no hidden panels.
Each slider has: label, live numeric readout (2-3 decimal places), and a
one-line physical description in small muted text beneath it.

| Slider | Label | Range | Default | Unit | Description |
|---|---|---|---|---|---|
| alpha | Sticking Probability | 0.01–1.00 | 0.55 | — | Electrolyte deposition aggressiveness |
| charge_rate | Charge Rate | 1–20 | 6 | particles/step | Maps to real current density via Faraday's Law |
| temperature_gradient | Temperature Gradient | 0.0–1.0 | 0.50 | — | Spatial heat intensity — hot center drives faster growth |
| num_cycles | Cycles to Simulate | 50–500 | 200 | cycles | Each cycle = one real charge event |
| ensemble_runs | Ensemble Runs | 1–100 | 50 | runs | Repeat runs averaged to remove stochastic noise |
| degradation_rate | Degradation Rate | 0.000–0.010 | 0.002 | per cycle | Electrolyte decay — raises alpha each cycle |
| sep_factor | Separator Resistance | 0.1–1.0 | 0.65 | — | Ion slowdown near cathode boundary (porosity) |
| edge_factor | Edge Enhancement | 1.0–2.0 | 1.25 | — | Extra ion flux at anode edges due to geometry |
| seed_roughness | Nucleation Roughness | 0.0–1.0 | 0.20 | — | Anode surface defect density — sets dendrite start sites |
| sei_growth_rate | SEI Growth Rate | 0.000–0.010 | 0.002 | per cycle | SEI layer thickening speed — reduces effective overpotential |

---

### Section 3 — Charge Profile Toggle

```
[ ⚡ FAST CHARGE   15 min ]      [ 🔋 SLOW CHARGE   60 min ]
```

Active = filled accent background. Inactive = outline only.
Fast charge sets: charge_rate=12, temp_gradient=0.70
Slow charge sets: charge_rate=3, temp_gradient=0.25
User can still override manually after clicking.

---

### Section 4 — Sand's Time Display

A read-only indicator panel below the charge toggle showing the
analytically computed Sand's Time for current parameters.

```
┌─────────────────────────────────────────────┐
│  SAND'S TIME                                │
│  τ = 847 seconds  →  Branching at step 2,34│
│  Status: ● SAFE (current rate below limit)  │
└─────────────────────────────────────────────┘
```

- Updates live as charge_rate slider moves
- Status dot: green when current charge rate is below Sand's limit
- Status dot: red when charge rate exceeds Sand's limit — branching inevitable
- τ value is computed by main.py and written to parameters.json as
  `sand_time_seconds` — read it from there, do not compute it yourself

---

### Section 5 — Simulation Control Buttons

```
[ ▶ RUN SIMULATION ]  [ ⏸ PAUSE ]  [ ↺ RESET ]  [ ⚙ RUN ENSEMBLE ]
```

- RUN: writes all slider values to parameters.json, signals simulation start,
  disables all sliders during run, re-enables on completion
- PAUSE: freezes simulation mid-run, preserves state
- RESET: stops simulation, clears grid, re-enables all sliders
- RUN ENSEMBLE: runs N times (ensemble_runs value), saves averaged output
  to data/simulation_output.csv

RUN button is visually dominant: larger, accent-colored fill, not outline.
All buttons have hover states.

---

### Section 6 — Live Status Bar

Thin strip at bottom of control panel. Updates every second during run.

```
● IDLE      Cycle: —       Risk: —      SEI: —       Sand: —
```

During run:

```
● RUNNING   Cycle: 47/200  Risk: 23.4%  SEI: 12nm    Sand: SAFE
```

After Sand's Time is crossed:

```
● RUNNING   Cycle: 91/200  Risk: 54.1%  SEI: 28nm    Sand: ⚠ BRANCHING
```

Color rules:
- Risk 0–40%: `#4ADE80`
- Risk 40–70%: `#FFB300`
- Risk 70–100%: `#FF4444` with pulse animation if possible
- SEI value: always golden `#FFD700`
- Sand status SAFE: `#00E5FF`
- Sand status BRANCHING: `#FF3333`

---

## Window 2 — Analytics Dashboard (`ui/analytics_dashboard.py`)

Matplotlib figure, multiple subplots in dashboard layout.
Launches after simulation completes, or in mock mode during development.

```bash
python ui/analytics_dashboard.py --mock
```

All charts read from mock CSVs during development.
On integration day the CSVs are replaced with real output.
Your code must not change on integration day.

---

### Dashboard Layout

```
┌──────────────────────────┬──────────────────────────┐
│  Chart 1                 │  Chart 2                 │
│  Dendrite Growth Curves  │  Short-Circuit Risk Score│
├──────────────────────────┼──────────────────────────┤
│  Chart 3                 │  Chart 4                 │
│  Anode Spatial Profile   │  Cycle-Life Comparison   │
├──────────────────────────┼──────────────────────────┤
│  Chart 5                 │  Chart 6                 │
│  Degradation Acceleration│  Ion Concentration Field │
├──────────────────────────┴──────────────────────────┤
│  Chart 7 (full width)                               │
│  SEI Layer Thickness Over Cycles                    │
├─────────────────────────────────────────────────────┤
│  Chart 8 (full width)                               │
│  Sand's Time Threshold Map                          │
└─────────────────────────────────────────────────────┘
```

---

### Chart Specifications

**Chart 1 — Dendrite Growth Curves**
- X: cycle number 0–200
- Y: max dendrite height as % of grid height
- Lines: fast charge (red tones) + slow charge (blue tones) for all 4 presets
- Dashed horizontal line at 78%: "Short-circuit threshold"
- Vertical dotted line where fast charge first crosses threshold: "SC risk: cycle N"
- Legend outside chart right side

**Chart 2 — Short-Circuit Risk Score**
- X: cycle number
- Y: risk score 0–100
- One line per preset: Fresh=green, Slight=yellow, Moderate=orange, Degraded=red
- Filled area under each curve at 15% opacity
- Horizontal threshold lines at 40 (amber) and 70 (red)

**Chart 3 — Anode Spatial Profile**
- X: anode position 0–100% of width
- Y: mean dendrite height in cells
- Fast charge = red filled area, slow charge = blue filled area
- Mark peak of each curve: dot + annotation "Peak degradation zone"
- Secondary shaded band showing where SEI is thickest (golden overlay)

**Chart 4 — Cycle-Life Comparison Bar Chart**
- Horizontal bar chart
- 8 bars: 4 presets × 2 charge rates
- X: cycles until risk score exceeds 70%
- Red bars = fast charge, blue bars = slow charge
- Each bar labeled with exact cycle count

**Chart 5 — Degradation Acceleration**
- X: cycle number
- Y: growth rate (rolling derivative of height per cycle)
- Lines: fast vs slow for moderately used preset
- Shade region above threshold: "Accelerated degradation zone" in red low opacity
- Mark Sand's Time crossing with vertical line: "Branching onset"

**Chart 6 — Ion Concentration Field Over Time**
- X: cycle number
- Y: mean local concentration near dendrite tips (0.0–1.0)
- Two lines: fast charge vs slow charge
- Shade below a depletion threshold (e.g. 0.3): "Depletion zone — branching risk"
- Annotate: "Concentration depletion accelerates after cycle N"
- This chart shows the mass transport limitation becoming active
- Data column in CSV: `conc_fast`, `conc_slow` (mean tip concentration per cycle)

**Chart 7 — SEI Layer Thickness (full width)**
- X: cycle number
- Y: mean SEI thickness in nanometers
- Four lines, one per preset, colored by preset color scheme
- Secondary Y axis (right): cumulative lithium loss % due to SEI consumption
- Shade region above critical SEI thickness with golden low opacity:
  "High resistance regime"
- Annotation: "SEI resistance reduces effective overpotential by X% at cycle N"
- Data columns: `sei_fresh`, `sei_slight`, `sei_moderate`, `sei_degraded`
  (mean SEI thickness in nm per cycle per preset)

**Chart 8 — Sand's Time Threshold Map (full width)**
- X: charge rate (particles/step, 1–20)
- Y: temperature gradient (0.0–1.0)
- This is a 2D heatmap — a grid of (charge_rate, temp_gradient) combinations
- Color: green where Sand's Time > cycle duration (branching won't occur),
  red where Sand's Time < cycle duration (branching inevitable)
- Mark current simulation parameters as a white dot with label "Current config"
- Contour line showing exact Sand's Time boundary
- Title: "Operating conditions that trigger dendrite branching"
- This is the most analytically powerful chart — it tells an engineer
  exactly which charge rates are safe at which temperatures
- Data file: `data/mock_sands_map.csv` — a 20×20 grid of 0/1 values
  (0=safe, 1=branching) — Tech Lead generates this

---

### Chart Styling

```python
plt.style.use('dark_background')
fig.patch.set_facecolor('#0a0a12')
ax.set_facecolor('#0d0d1a')
ax.grid(True, color='#1e1e3a', linewidth=0.5, alpha=0.8)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_edgecolor('#1e1e3a')
ax.tick_params(colors='#666688', labelsize=9)
ax.xaxis.label.set_color('#8888aa')
ax.yaxis.label.set_color('#8888aa')
ax.set_title('Title', color='#ccccee', fontsize=11, fontweight='normal', pad=12)
```

Color palettes:
```python
FAST_COLORS  = ['#FF4444', '#FF6B35', '#FF8C42', '#FFA500']
SLOW_COLORS  = ['#4FC3F7', '#29B6F6', '#0288D1', '#01579B']
PRESET_COLORS = {
    'fresh':    '#4ADE80',
    'slight':   '#FFB300',
    'moderate': '#FF8C42',
    'degraded': '#FF4444'
}
SEI_COLOR    = '#FFD700'
SAND_SAFE    = '#00E5FF'
SAND_BRANCH  = '#FF3333'
DEPLETE_COLOR = '#AA44FF'
```

---

## Window 3 — Export and Report Generation

### PNG Export

```
outputs/chart1_growth_curves.png
outputs/chart2_risk_scores.png
outputs/chart3_spatial_profile.png
outputs/chart4_cycle_life_comparison.png
outputs/chart5_degradation_acceleration.png
outputs/chart6_concentration_field.png
outputs/chart7_sei_thickness.png
outputs/chart8_sands_map.png
```

300 DPI minimum. 1200×800px per chart minimum.

### Report Summary Export

Generates `report/simulation_summary.txt`:

```
DENDRITE ENGINE — SIMULATION RESULTS SUMMARY
=============================================
Run date: [date]
Target cell: LG M50 INR21700
Simulation cycles: [N]
Ensemble runs: [N]

FAST CHARGE RESULTS
-------------------
Fresh battery:        SC risk threshold at cycle [N]
Slightly used:        SC risk threshold at cycle [N]
Moderately used:      SC risk threshold at cycle [N]
Heavily degraded:     SC risk threshold at cycle [N]

SLOW CHARGE RESULTS
-------------------
Fresh battery:        SC risk threshold at cycle [N]
Slightly used:        SC risk threshold at cycle [N]
Moderately used:      SC risk threshold at cycle [N]
Heavily degraded:     SC risk threshold at cycle [N]

SEI ANALYSIS
------------
Mean SEI thickness at cycle 200 (fast, moderately used): [X] nm
Cumulative lithium loss to SEI (fast, moderately used):  [X]%
SEI resistance contribution to overpotential reduction:  [X]%

MASS TRANSPORT
--------------
Ion concentration depletion below 0.3 threshold: cycle [N] (fast charge)
Ion concentration depletion below 0.3 threshold: cycle [N] (slow charge)

SAND'S TIME
-----------
Sand's Time for fast charge conditions: [X] seconds
Sand's Time for slow charge conditions: [X] seconds
Branching onset cycle (fast charge): [N]
Branching onset cycle (slow charge): N/A — Sand's Time not reached

KEY FINDING
-----------
Fast charging reduces safe cycle life by [X]% vs slow charging
under moderately used battery conditions.

Peak degradation zone: [X]% from anode left edge (fast charge)
Peak degradation zone: [X]% from anode left edge (slow charge)
```

---

## Cycle Scrubber

Horizontal slider below dashboard after a completed run.

```
Cycle:  [====|=================]  47 / 200
```

Dragging updates Chart 3 spatial profile to show anode state at that cycle.
Simulation saves spatial snapshots every 10 cycles — Tech Lead handles this.
You read from `data/spatial_snapshots/snapshot_cycle_NNN.csv`.

---

## Mock Data Contract

Column names are locked. Do not rename. Do not reorder.

`data/mock_output.csv`:
```
cycle
fresh_fast, slight_fast, moderate_fast, degraded_fast
fresh_slow, slight_slow, moderate_slow, degraded_slow
risk_fresh_fast, risk_slight_fast, risk_moderate_fast, risk_degraded_fast
risk_fresh_slow, risk_slight_slow, risk_moderate_slow, risk_degraded_slow
conc_fast, conc_slow
sei_fresh, sei_slight, sei_moderate, sei_degraded
sand_crossed_cycle_fast, sand_crossed_cycle_slow
```

`data/mock_spatial.csv`:
```
anode_x
fresh_fast_profile, slight_fast_profile, moderate_fast_profile, degraded_fast_profile
fresh_slow_profile, slight_slow_profile, moderate_slow_profile, degraded_slow_profile
sei_profile_fast, sei_profile_slow
```

`data/mock_sands_map.csv`:
```
charge_rate, temp_gradient, branching_flag
(20×20 grid of all combinations, branching_flag = 0 or 1)
```

---

## Performance Rules

- Do NOT import taichi, numba, or anything from core/
- Use plt.pause() not plt.show() for live updates
- Control panel communicates with simulation only via parameters.json
  and a status file — no direct function calls
- Poll parameters.json maximum once per second
- Use fig.tight_layout() and plt.subplots_adjust() on every figure
- Sand's Time value is read from parameters.json field `sand_time_seconds`
  — do not recompute it yourself

---

## Deliverable Checklist

| Item | File | Done |
|---|---|---|
| Control panel window opens | control_panel.py | ⬜ |
| All 10 sliders functional with live readout | control_panel.py | ⬜ |
| 4 preset buttons load full parameter bundles | control_panel.py | ⬜ |
| Fast/Slow charge toggle working | control_panel.py | ⬜ |
| Sand's Time display panel updates live | control_panel.py | ⬜ |
| Run/Pause/Reset/Ensemble buttons present | control_panel.py | ⬜ |
| Live status bar shows Risk + SEI + Sand | control_panel.py | ⬜ |
| Dashboard opens in mock mode | analytics_dashboard.py | ⬜ |
| Charts 1–6 rendering with correct data | analytics_dashboard.py | ⬜ |
| Chart 7 SEI thickness with dual Y axis | analytics_dashboard.py | ⬜ |
| Chart 8 Sand's Time heatmap rendering | analytics_dashboard.py | ⬜ |
| Dark premium styling on all charts | analytics_dashboard.py | ⬜ |
| PNG export at 300 DPI for all 8 charts | analytics_dashboard.py | ⬜ |
| Report summary text file generated | analytics_dashboard.py | ⬜ |
| SEI and Sand metrics in report summary | analytics_dashboard.py | ⬜ |
| Cycle scrubber functional | analytics_dashboard.py | ⬜ |

---

## Day-by-Day Targets

| Day | Target |
|---|---|
| 1 | Control panel opens with all 10 sliders. Charts 1 and 2 render in mock mode. |
| 2 | Charts 3–6 rendering. Preset buttons loading correct bundles. Sand's Time panel displaying. |
| 3 | Charts 7 and 8 rendering. Dark styling applied to all. Fast/Slow toggle working. |
| 4 | Export functional for all 8 charts. Status bar showing SEI and Sand values live. |
| 5 | Report summary generation complete. Cycle scrubber working. Full styling polish. |
| 6 | Integration day — swap mock CSVs for real output. Verify nothing breaks. |

---

*If anything is unclear, ask the Tech Lead before building.
Do not assume data format — the mock CSV is the contract.
Do not compute Sand's Time or SEI values yourself — read them from the CSV.*
