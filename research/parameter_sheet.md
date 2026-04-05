# Parameter Sheet — Dendrite Engine
## Research Team Deliverable

Every entry requires: the value, the unit, the paper/source title, and a DOI or URL.
No value without a source. Priorities 1, 2, 3 must be completed before Day 4.
Everything else by Day 5.

---

## Priority 1 — Simulation Blocker

| Parameter | Symbol | Unit | Target Range | Search Terms | Value | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| Li⁺ diffusion coefficient in LiPF6 EC:DMC electrolyte | D₀ | m²/s | 10⁻¹⁰ to 10⁻⁹ | "lithium ion diffusion coefficient LiPF6 EC DMC" | | | | ⬜ |

---

## Priority 2 — Calibration Blockers (find all three together, they're in the same datasheet)

| Parameter | Symbol | Unit | Target Range | Search Terms | Value | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| Anode surface area of target cell | A | mm² | — | "LG M50 INR21700 datasheet teardown" | | | | ⬜ |
| Fast charge current | I_fast | A | — | "LG M50 INR21700 datasheet" | | | | ⬜ |
| Slow charge current (standard) | I_slow | A | — | "LG M50 INR21700 datasheet" | | | | ⬜ |

---

## Priority 3 — Validation Benchmark

| Parameter | Symbol | Unit | Target Range | Search Terms | Value | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| Cycle life to 80% capacity retention | N_rated | cycles | 300–800 | "LG M50 cycle life capacity retention" | | | | ⬜ |

---

## Priority 4 — Temperature Physics

| Parameter | Symbol | Unit | Target Range | Search Terms | Value | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| Activation energy for Li⁺ diffusion | Eₐ | kJ/mol | 15–30 | "activation energy Li diffusion electrolyte Arrhenius" | | | | ⬜ |
| Internal temperature rise during fast charge | ΔT | °C | 3–8 | "battery internal temperature fast charging thermal" | | | | ⬜ |

---

## Priority 5 — Alpha Calibration (Butler-Volmer)

| Parameter | Symbol | Unit | Target Range | Search Terms | Value | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| Exchange current density | i₀ | A/m² | — | "Butler-Volmer exchange current density lithium graphite anode" | | | | ⬜ |
| Anodic transfer coefficient | αₐ | — | ~0.5 | "Butler-Volmer transfer coefficient lithium deposition" | | | | ⬜ |
| Cathodic transfer coefficient | αc | — | ~0.5 | "Butler-Volmer transfer coefficient lithium deposition" | | | | ⬜ |

---

## Priority 6 — Degradation Dynamics

| Parameter | Symbol | Unit | Target Range | Search Terms | Value | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| Electrolyte degradation rate per cycle | k_deg | per cycle | 0.001–0.005 | "electrolyte degradation rate capacity fade lithium ion cycle" | | | | ⬜ |
| Current density edge enhancement factor | f_edge | — | 1.1–1.4 | "current distribution non-uniformity lithium ion anode edge" | | | | ⬜ |

---

## Priority 7 — Separator Physics

| Parameter | Symbol | Unit | Target Range | Search Terms | Value | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| Separator porosity resistance factor | f_sep | — | 0.3–0.7 | "separator porosity resistance lithium ion dendrite growth" | | | | ⬜ |

---

## Priority 8 — Report Evidence (no code impact)

| Parameter | Symbol | Unit | Notes | Search Terms | Found | Source | DOI/URL | Status |
|---|---|---|---|---|---|---|---|---|
| SEM images of Li dendrites on graphite anode | — | — | Need cross-section images from fast-charge abuse studies | "lithium dendrite SEM graphite anode fast charge" | | | | ⬜ |
| Electrolyte ionic conductivity vs temperature | σ(T) | S/m | Table or graph form preferred | "LiPF6 EC DMC conductivity temperature dependence" | | | | ⬜ |

---

## How to Fill This In

1. Find the value from a published paper or official manufacturer datasheet
2. Write the exact numeric value and unit in the Value column
3. Write the paper title or datasheet name in the Source column
4. Paste the DOI (e.g. `10.1016/j.electacta.2019.xx`) or full URL in the DOI/URL column
5. Change ⬜ to ✅ when complete

## Target Cell

**LG M50 INR21700** — used in Tesla Model 3 long range pack.
Well-documented in public literature and third-party teardown studies.
All Priority 2 parameters should come from the same source for consistency.

## Notes for the Research Team

- D₀ varies with temperature. Find the value at 25°C specifically.
- I_fast and I_slow are in Amperes for the full cell, not current density.
  The Tech Lead will convert to current density using anode surface area.
- For Butler-Volmer parameters, the same paper will usually report
  i₀, αₐ, and αc together. Find one good source for all three.
- SEM images do not need a numeric value — just a citable source
  with a figure we can reference in the report.