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

## Aesthetic Direction

**Dark. Premium. Ambient.**

- Background: near-black, not pure black. Use `#0a0a12` or `#080810`
- Accent color: electric blue `#4FC3F7` for active elements, highlights, borders
- Secondary accent: amber `#FFB300` for warnings and critical risk indicators
- Danger color: `#FF4444` for short-circuit risk threshold crossings
- Success color: `#4ADE80` for safe/low-risk states
- All panels: dark surface `#12121e` with a `1px` border in `#1e1e3a`
- Typography: use a monospace or technical font for numbers and data readouts.
  `Consolas` or `Courier New` is fine since this is Python/Matplotlib.
  No default Arial or sans-serif on data labels.
- Gradients: use them on chart fills, backgrounds, and button hover states.
  Flat solid colors should be the exception, not the rule.
- No white backgrounds anywhere. Not on panels, not on charts, not on popups.

The reference aesthetic is: a Bloomberg terminal crossed with a high-end
scientific instrument interface. Every number should feel like it means
something. Every chart should feel like it cost money to produce.

---

## Window 1 — Control Panel (`ui/control_panel.py`)

This is a standalone Python window built in Tkinter or PyQt5.
It launches before the simulation starts.
It writes values to `data/parameters.json` when the user clicks Run.
It does NOT import anything from `core/` or `renderer/`.

### Required Elements

#### Battery Age Preset Selector
Four large clickable buttons, horizontally arranged, at the top of the panel.

```
[ FRESH ]  [ SLIGHTLY USED ]  [ MODERATELY USED ]  [ HEAVILY DEGRADED ]
```

Clicking one loads a full parameter bundle into all sliders simultaneously.
The active preset button should glow with the accent border.
This is the most important UX element. It must work perfectly.

Preset parameter bundles to load (these map to the sliders below):

| Preset | alpha | charge_rate | temp_gradient | degradation_rate |
|---|---|---|---|---|
| Fresh | 0.15 | 3 | 0.20 | 0.001 |
| Slightly used | 0.30 | 5 | 0.40 | 0.002 |
| Moderately used | 0.50 | 8 | 0.65 | 0.003 |
| Heavily degraded | 0.75 | 12 | 0.85 | 0.005 |

#### Parameter Sliders
Six sliders, each with a label, a live numeric readout, and a physical
description in small text beneath it. All displayed simultaneously —
no tabs, no hidden panels.

| Slider | Label | Range | Default | Unit | Description shown to user |
|---|---|---|---|---|---|
| alpha | Sticking Probability | 0.01 – 1.00 | 0.55 | — | Electrolyte deposition aggressiveness |
| charge_rate | Charge Rate | 1 – 20 | 6 | particles/step | Maps to real current density |
| temperature_gradient | Temperature Gradient | 0.0 – 1.0 | 0.50 | — | Spatial heat distribution intensity |
| num_cycles | Cycles to Simulate | 50 – 500 | 200 | cycles | Each cycle = one charge event |
| ensemble_runs | Ensemble Runs | 1 – 100 | 50 | runs | Repeat runs averaged for stability |
| degradation_rate | Degradation Rate | 0.000 – 0.010 | 0.002 | per cycle | Electrolyte decay speed per cycle |

Sliders must update the numeric readout in real time as they move.
Numeric readout must show 2-3 decimal places, not integers.

#### Charge Profile Selector
Two large toggle buttons below the sliders:

```
[ ⚡ FAST CHARGE  15 min ]     [ 🔋 SLOW CHARGE  60 min ]
```

Active selection has a filled accent background.
Inactive has outline only.
This sets the charge_rate slider automatically when clicked, but the user
can still override it manually.

#### Simulation Control Buttons
Four buttons at the bottom of the panel:

```
[ ▶ RUN SIMULATION ]  [ ⏸ PAUSE ]  [ ↺ RESET ]  [ ⚙ RUN ENSEMBLE ]
```

- RUN: writes current slider values to `parameters.json`, signals simulation
  to start, disables all sliders during run (re-enables on completion)
- PAUSE: freezes the simulation mid-run without resetting state
- RESET: stops simulation, clears grid, re-enables sliders
- RUN ENSEMBLE: runs the simulation N times (ensemble_runs value) and saves
  averaged output to `data/simulation_output.csv`

Buttons must have hover states. RUN button should be visually dominant —
larger, accent-colored background, not just an outline.

#### Live Status Bar
A thin strip at the very bottom of the control panel showing:

```
● IDLE        Cycle: —        Risk: —        Height: —
```

Updates every second during a run:

```
● RUNNING     Cycle: 47/200   Risk: 23.4%    Height: 142 cells
```

Risk score text color changes dynamically:
- 0–40%: green `#4ADE80`
- 40–70%: amber `#FFB300`
- 70–100%: red `#FF4444` with a subtle pulse animation if possible

---

## Window 2 — Analytics Dashboard (`ui/analytics_dashboard.py`)

This is a Matplotlib figure with multiple subplots arranged in a dashboard
layout. It launches after a simulation run completes, or in mock mode for
development.

All charts read from `data/mock_output.csv` and `data/mock_spatial.csv`
during development. On integration day these files are replaced with real
simulation output. Your code must not change.

### Running in Mock Mode (how you develop before integration)

```python
python ui/analytics_dashboard.py --mock
```

This loads mock CSV data. Real mode (no flag) loads actual simulation output.
Build and test everything in mock mode.

### Dashboard Layout

```
┌─────────────────────────────┬─────────────────────────────┐
│  Chart 1                    │  Chart 2                    │
│  Dendrite Growth Curves     │  Short-Circuit Risk Score   │
│  (fast vs slow, all presets)│  (by age state over cycles) │
├─────────────────────────────┼─────────────────────────────┤
│  Chart 3                    │  Chart 4                    │
│  Anode Spatial Profile      │  Cycle-Life Comparison Bar  │
│  (height across anode width)│  (fast vs slow, 4 presets)  │
├─────────────────────────────┴─────────────────────────────┤
│  Chart 5 (full width)                                     │
│  Degradation Acceleration — Growth Rate per Cycle         │
│  (derivative of Chart 1 — shows where growth speeds up)   │
└───────────────────────────────────────────────────────────┘
```

### Chart Specifications

**Chart 1 — Dendrite Growth Curves**
- X axis: cycle number (0–200)
- Y axis: max dendrite height as % of grid height (0–100%)
- Lines: fast charge (red tones) and slow charge (blue tones) for each preset
- Dashed horizontal line at 78% labeled "Short-circuit threshold"
- Where fast charge crosses the threshold: mark with a vertical dotted line
  and annotate "SC risk: cycle N"
- Legend: outside chart, right side

**Chart 2 — Short-Circuit Risk Score**
- X axis: cycle number
- Y axis: risk score 0–100
- One line per battery age preset, color coded:
  Fresh=green, Slightly used=yellow, Moderate=orange, Degraded=red
- Filled area under each curve with 15% opacity matching line color
- Horizontal threshold lines at 40 (amber) and 70 (red) labeled

**Chart 3 — Anode Spatial Profile**
- X axis: anode position left to right (0–100% of anode width)
- Y axis: mean dendrite height in cells
- Two filled area curves: fast charge (red fill) vs slow charge (blue fill)
- Mark the peak of each curve with a dot and annotate the x-position:
  "Peak degradation zone"
- This chart shows WHERE on the anode failure concentrates

**Chart 4 — Cycle-Life Comparison Bar Chart**
- Horizontal bar chart
- Y axis: 8 bars (4 presets × 2 charge rates)
- X axis: cycles until risk score exceeds 70%
- Color: red bars for fast charge, blue bars for slow charge
- Each bar labeled with its exact cycle count
- This is the most immediately readable chart for non-technical audiences

**Chart 5 — Degradation Acceleration**
- X axis: cycle number
- Y axis: growth rate (height change per cycle, computed as rolling derivative)
- Lines: fast charge vs slow charge for the moderately used preset
- Shade the region where growth rate exceeds a threshold as "Accelerated
  degradation zone" in red with low opacity
- This shows the non-linear acceleration — the key scientific finding

### Chart Styling (applies to all five charts)

```python
# Apply this style to every chart
plt.style.use('dark_background')

# Figure background
fig.patch.set_facecolor('#0a0a12')

# Axes background
ax.set_facecolor('#0d0d1a')

# Grid lines: subtle, not distracting
ax.grid(True, color='#1e1e3a', linewidth=0.5, alpha=0.8)
ax.set_axisbelow(True)

# Spine colors
for spine in ax.spines.values():
    spine.set_edgecolor('#1e1e3a')

# Tick colors
ax.tick_params(colors='#666688', labelsize=9)

# Axis label colors
ax.xaxis.label.set_color('#8888aa')
ax.yaxis.label.set_color('#8888aa')

# Title style
ax.set_title('Chart Title', color='#ccccee',
             fontsize=11, fontweight='normal', pad=12)
```

Color palette for data lines:
```python
FAST_COLORS = ['#FF4444', '#FF6B35', '#FF8C42', '#FFA500']  # red to amber
SLOW_COLORS = ['#4FC3F7', '#29B6F6', '#0288D1', '#01579B']  # light to deep blue
PRESET_COLORS = {
    'fresh': '#4ADE80',
    'slight': '#FFB300',
    'moderate': '#FF8C42',
    'degraded': '#FF4444'
}
```

---

## Window 3 — Export and Report Generation

A simple export panel, launchable from a button in the analytics dashboard.

### PNG Export
Saves each of the 5 charts as individual high-resolution PNG files:

```
outputs/chart1_growth_curves.png
outputs/chart2_risk_scores.png
outputs/chart3_spatial_profile.png
outputs/chart4_cycle_life_comparison.png
outputs/chart5_degradation_acceleration.png
```

Resolution: 300 DPI minimum. These go directly into the LaTeX report.
Size: 1200×800px per chart minimum.

### Report Summary Export
Generates a plain text file at `report/simulation_summary.txt` containing:

```
DENDRITE ENGINE — SIMULATION RESULTS SUMMARY
=============================================
Run date: [date]
Target cell: LG M50 INR21700
Simulation cycles: 200
Ensemble runs: 50

FAST CHARGE RESULTS
-------------------
Fresh battery:         SC risk threshold at cycle [N]
Slightly used:         SC risk threshold at cycle [N]
Moderately used:       SC risk threshold at cycle [N]
Heavily degraded:      SC risk threshold at cycle [N]

SLOW CHARGE RESULTS
-------------------
Fresh battery:         SC risk threshold at cycle [N]
Slightly used:         SC risk threshold at cycle [N]
Moderately used:       SC risk threshold at cycle [N]
Heavily degraded:      SC risk threshold at cycle [N]

KEY FINDING
-----------
Fast charging reduces safe cycle life by [X]% relative to slow charging
under moderately used battery conditions.

Peak degradation zone: [X]% from anode left edge (fast charge)
Peak degradation zone: [X]% from anode left edge (slow charge)
```

The Tech Lead converts this file into LaTeX. You just need to generate it
with the correct numbers pulled from the simulation output CSV.

---

## Cycle Scrubber (Post-Run Feature)

After a full simulation run, a horizontal slider appears below the dashboard:

```
Cycle:  [====|=================]  47 / 200
```

Dragging it updates Chart 3 (spatial profile) to show the anode state at
that specific cycle. Requires that the simulation saves a spatial snapshot
every 10 cycles during the run (the Tech Lead handles saving this data —
you just need to read and display it).

---

## The Mock Data Contract

The columns in `data/mock_output.csv` are locked. Do not rename them.
Do not reorder them. Your code must read these exact column names:

```
cycle
fresh_fast, slight_fast, moderate_fast, degraded_fast
fresh_slow,  slight_slow,  moderate_slow,  degraded_slow
risk_fresh_fast, risk_slight_fast, risk_moderate_fast, risk_degraded_fast
risk_fresh_slow, risk_slight_slow, risk_moderate_slow, risk_degraded_slow
```

The columns in `data/mock_spatial.csv`:

```
anode_x
fresh_fast_profile, slight_fast_profile, moderate_fast_profile, degraded_fast_profile
fresh_slow_profile, slight_slow_profile, moderate_slow_profile, degraded_slow_profile
```

On integration day, these files are replaced with real simulation output.
If your code reads these column names correctly, nothing else changes.

---

## Performance Rules

- The dashboard must not import taichi, numba, or anything from core/
- All chart rendering must be non-blocking — use plt.pause() not plt.show()
  if displaying live updates
- The control panel runs in its own process — it communicates with the
  simulation only through parameters.json and a simple status file
- Do not poll parameters.json more than once per second
- All Matplotlib figures must use fig.tight_layout() and
  plt.subplots_adjust() to prevent label clipping on any screen size

---

## Deliverable Checklist

| Item | File | Done |
|---|---|---|
| Control panel window opens | control_panel.py | ⬜ |
| All 6 sliders functional with live readout | control_panel.py | ⬜ |
| 4 preset buttons load correct parameter bundles | control_panel.py | ⬜ |
| Fast/Slow charge toggle working | control_panel.py | ⬜ |
| Run/Pause/Reset/Ensemble buttons present | control_panel.py | ⬜ |
| Live status bar updates during run | control_panel.py | ⬜ |
| Dashboard opens in mock mode | analytics_dashboard.py | ⬜ |
| All 5 charts render with correct data | analytics_dashboard.py | ⬜ |
| Dark premium styling applied to all charts | analytics_dashboard.py | ⬜ |
| PNG export at 300 DPI | analytics_dashboard.py | ⬜ |
| Report summary text file generated | analytics_dashboard.py | ⬜ |
| Cycle scrubber functional | analytics_dashboard.py | ⬜ |
| All charts readable on dark background | analytics_dashboard.py | ⬜ |

---

## Day-by-Day Targets

| Day | Target |
|---|---|
| 1 | Control panel window opens with all sliders. Mock dashboard loads and displays Chart 1. |
| 2 | All 5 charts rendering in mock mode. Preset buttons working. |
| 3 | Dark styling applied to all charts. Export buttons functional. |
| 4 | Status bar live updates. Cycle scrubber working against mock snapshots. |
| 5 | Report summary generation working. Full polish pass on all styling. |
| 6 | Integration day — swap mock CSV for real output. Verify nothing breaks. |

---

*If anything in this brief is unclear, ask the Tech Lead before building.
Do not make assumptions about data format — the mock CSV is the contract.*
```