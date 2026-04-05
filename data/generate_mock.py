import numpy as np
import pandas as pd

np.random.seed(42)
cycles = np.arange(1, 201)

def growth_curve(base_rate, accel, noise_std):
    height = base_rate * cycles + accel * cycles**2 * 0.001
    height += np.random.normal(0, noise_std, len(cycles))
    height = np.clip(height, 0, 95)
    return np.round(height, 2)

data = {
    'cycle': cycles,
    'fresh_fast':        growth_curve(0.30, 1.8, 1.2),
    'slight_fast':       growth_curve(0.42, 2.4, 1.5),
    'moderate_fast':     growth_curve(0.58, 3.5, 2.0),
    'degraded_fast':     growth_curve(0.80, 5.2, 2.8),
    'fresh_slow':        growth_curve(0.10, 0.5, 0.6),
    'slight_slow':       growth_curve(0.15, 0.8, 0.8),
    'moderate_slow':     growth_curve(0.22, 1.2, 1.0),
    'degraded_slow':     growth_curve(0.38, 2.1, 1.4),
}

df = pd.DataFrame(data)

for col in [c for c in df.columns if c != 'cycle']:
    df[f'risk_{col}'] = np.round(df[col] / 95 * 100, 1)

df.to_csv('data/mock_output.csv', index=False)
print(f"mock_output.csv written: {len(df)} rows, {len(df.columns)} columns")

anode_positions = np.arange(0, 400)
spatial_data = {'anode_x': anode_positions}

for preset in ['fresh', 'slight', 'moderate', 'degraded']:
    for rate in ['fast', 'slow']:
        amplitude = {'fresh': 25, 'slight': 38,
                     'moderate': 55, 'degraded': 75}[preset]
        if rate == 'slow':
            amplitude *= 0.45
        heat_bias = {'fresh': 0.3, 'slight': 0.5,
                     'moderate': 0.7, 'degraded': 0.9}[preset]
        profile = amplitude * (1 - np.abs(anode_positions - 200)
                  / 200 * (1 - heat_bias))
        profile += np.random.normal(0, amplitude * 0.08, 400)
        profile = np.clip(profile, 0, None)
        spatial_data[f'{preset}_{rate}_profile'] = np.round(profile, 1)

pd.DataFrame(spatial_data).to_csv('data/mock_spatial.csv', index=False)
print(f"mock_spatial.csv written")