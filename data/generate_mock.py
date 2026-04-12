import numpy as np
import pandas as pd
import itertools
import os

np.random.seed(42)
cycles = np.arange(1, 201)

# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

def growth_curve(base_rate, accel, noise_std, seed=None):
    if seed:
        np.random.seed(seed)
    height = base_rate * cycles + accel * cycles**2 * 0.001
    height += np.random.normal(0, noise_std, len(cycles))
    return np.clip(np.round(height, 2), 0, 95)

def concentration_curve(depletion_start, depletion_rate, noise_std):
    # starts at 1.0, depletes faster after depletion_start cycle
    conc = np.ones(len(cycles))
    for i, c in enumerate(cycles):
        if c > depletion_start:
            conc[i] = max(0.05, 1.0 - depletion_rate *
                         (c - depletion_start) + 
                         np.random.normal(0, noise_std))
        else:
            conc[i] = min(1.0, 1.0 + np.random.normal(0, noise_std * 0.3))
    return np.round(conc, 3)

def sei_curve(growth_coeff, noise_std, seed=None):
    # parabolic SEI growth law: L = L0 * sqrt(N) * coeff
    # returns thickness in nanometers
    if seed:
        np.random.seed(seed)
    thickness = growth_coeff * np.sqrt(cycles) * 8.0
    thickness += np.random.normal(0, noise_std, len(cycles))
    return np.clip(np.round(thickness, 2), 0, None)

def lithium_loss_curve(sei_thickness):
    # cumulative lithium loss % derived from SEI thickness
    return np.round(sei_thickness * 0.18, 2)

# ─────────────────────────────────────────────
# mock_output.csv
# ─────────────────────────────────────────────

data = {
    'cycle': cycles,

    # dendrite height per cycle (% of grid height)
    'fresh_fast':        growth_curve(0.30, 1.8, 1.2, seed=1),
    'slight_fast':       growth_curve(0.42, 2.4, 1.5, seed=2),
    'moderate_fast':     growth_curve(0.58, 3.5, 2.0, seed=3),
    'degraded_fast':     growth_curve(0.80, 5.2, 2.8, seed=4),
    'fresh_slow':        growth_curve(0.10, 0.5, 0.6, seed=5),
    'slight_slow':       growth_curve(0.15, 0.8, 0.8, seed=6),
    'moderate_slow':     growth_curve(0.22, 1.2, 1.0, seed=7),
    'degraded_slow':     growth_curve(0.38, 2.1, 1.4, seed=8),
}

df = pd.DataFrame(data)

# risk scores derived from height
for col in [c for c in df.columns if c != 'cycle']:
    df[f'risk_{col}'] = np.round(df[col] / 95 * 100, 1)

# ion concentration near dendrite tips
# fast charge depletes concentration earlier and more aggressively
df['conc_fast'] = concentration_curve(
    depletion_start=60, depletion_rate=0.008, noise_std=0.015)
df['conc_slow'] = concentration_curve(
    depletion_start=130, depletion_rate=0.003, noise_std=0.008)

# SEI thickness in nanometers per preset
# degraded batteries have thicker initial SEI that grows faster
df['sei_fresh']    = sei_curve(0.60, 0.8,  seed=11)
df['sei_slight']   = sei_curve(0.85, 1.2,  seed=12)
df['sei_moderate'] = sei_curve(1.20, 1.8,  seed=13)
df['sei_degraded'] = sei_curve(1.80, 2.5,  seed=14)

# cumulative lithium loss % from SEI for each preset
df['li_loss_fresh']    = lithium_loss_curve(df['sei_fresh'])
df['li_loss_slight']   = lithium_loss_curve(df['sei_slight'])
df['li_loss_moderate'] = lithium_loss_curve(df['sei_moderate'])
df['li_loss_degraded'] = lithium_loss_curve(df['sei_degraded'])

# Sand's Time crossing cycle
# fast charge hits Sand's limit around cycle 85 for moderate preset
# slow charge never crosses within 200 cycles
df['sand_crossed_fast'] = np.where(cycles >= 85, 1, 0)
df['sand_crossed_slow'] = np.zeros(len(cycles), dtype=int)

os.makedirs('data', exist_ok=True)
df.to_csv('data/mock_output.csv', index=False)
print(f"mock_output.csv written: {len(df)} rows, {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}")

# ─────────────────────────────────────────────
# mock_spatial.csv
# ─────────────────────────────────────────────

anode_x = np.arange(0, 400)
center = 200
spatial = {'anode_x': anode_x}

profiles = {
    'fresh':    {'amplitude_fast': 25,  'amplitude_slow': 11,
                 'heat_bias_fast': 0.30, 'heat_bias_slow': 0.15},
    'slight':   {'amplitude_fast': 38,  'amplitude_slow': 17,
                 'heat_bias_fast': 0.50, 'heat_bias_slow': 0.25},
    'moderate': {'amplitude_fast': 55,  'amplitude_slow': 25,
                 'heat_bias_fast': 0.70, 'heat_bias_slow': 0.35},
    'degraded': {'amplitude_fast': 75,  'amplitude_slow': 34,
                 'heat_bias_fast': 0.90, 'heat_bias_slow': 0.50},
}

for preset, vals in profiles.items():
    for rate in ['fast', 'slow']:
        amp       = vals[f'amplitude_{rate}']
        heat_bias = vals[f'heat_bias_{rate}']
        dist = np.abs(anode_x - center) / center
        profile = amp * (1 - dist * (1 - heat_bias))
        profile += np.random.normal(0, amp * 0.07, 400)
        profile = np.clip(profile, 0, None)
        spatial[f'{preset}_{rate}_profile'] = np.round(profile, 1)

# SEI spatial profiles — thicker in center hot zone
for rate in ['fast', 'slow']:
    base = 28.0 if rate == 'fast' else 14.0
    dist = np.abs(anode_x - center) / center
    sei_profile = base * (1 - dist * 0.4)
    sei_profile += np.random.normal(0, base * 0.05, 400)
    sei_profile = np.clip(sei_profile, 0, None)
    spatial[f'sei_profile_{rate}'] = np.round(sei_profile, 2)

pd.DataFrame(spatial).to_csv('data/mock_spatial.csv', index=False)
print(f"mock_spatial.csv written: {len(anode_x)} positions, "
      f"{len(spatial)} columns")

# ─────────────────────────────────────────────
# mock_sands_map.csv
# ─────────────────────────────────────────────
# 20x20 grid: charge_rate (1-20) x temp_gradient (0.05-1.0)
# branching_flag = 1 if Sand's Time < cycle duration, else 0
# Uses a simplified analytical estimate of Sand's Time

# placeholder constants — replace with real values when research team delivers
D0_PLACEHOLDER    = 3.0e-10   # m^2/s  Li+ diffusion coefficient
C0_PLACEHOLDER    = 1000.0    # mol/m³  bulk concentration (1M LiPF6)
L_ELECTROLYTE     = 25e-6     # m       electrolyte gap thickness
CYCLE_DURATION_S  = 2700.0    # seconds (45 min charge)
Z                 = 1
F                 = 96485.0

charge_rates   = np.linspace(1, 20, 20)
temp_gradients = np.linspace(0.05, 1.0, 20)

rows = []
for cr, tg in itertools.product(charge_rates, temp_gradients):
    # scale current density by charge rate and temperature gradient
    # higher temp = higher diffusion = slightly higher limiting current
    temp_factor  = 1.0 + tg * 0.3
    J_applied    = cr * 2.5 * temp_factor       # A/m² proxy
    J_lim        = (2 * Z * F * D0_PLACEHOLDER * C0_PLACEHOLDER
                    / L_ELECTROLYTE)             # limiting current density
    if J_applied <= J_lim:
        tau_sand = 1e9  # effectively infinite — never branches
    else:
        tau_sand = (np.pi * D0_PLACEHOLDER *
                    (Z * F * C0_PLACEHOLDER) ** 2 /
                    (4 * (J_applied - J_lim) ** 2))
    branching = 1 if tau_sand < CYCLE_DURATION_S else 0
    rows.append({
        'charge_rate':    round(cr, 2),
        'temp_gradient':  round(tg, 2),
        'tau_sand_s':     round(tau_sand, 1) if tau_sand < 1e8 else -1,
        'branching_flag': branching
    })

sands_df = pd.DataFrame(rows)
sands_df.to_csv('data/mock_sands_map.csv', index=False)
print(f"mock_sands_map.csv written: {len(sands_df)} rows "
      f"({len(charge_rates)}x{len(temp_gradients)} grid)")
print(f"Branching conditions: "
      f"{sands_df['branching_flag'].sum()} / {len(sands_df)} combinations")
