"""
make_lesion_figure.py

Generates a 2x2 grid of bar plots (Stroke, Tumour, MS, WMH),
showing mean ± SD for the first numeric metric (val1) by method type (Diffusion, AE, VAE, GAN),
using data loaded from Table2.csv.

Usage:
    python make_lesion_figure.py

Requires:
    - matplotlib
    - pandas
    - pillow
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# -------------------------
# Load data
# -------------------------
filename = "Table2.csv"
df = pd.read_csv(filename)

# Ensure consistent column names (handles if your CSV has unnamed columns)
expected_cols = ['author', 'disease', 'modality', 'method', 'dim', 'val1', 'val2', 'val3', 'notes']
if len(df.columns) < len(expected_cols):
    # Pad missing columns
    for i in range(len(df.columns), len(expected_cols)):
        df[expected_cols[i]] = ""
df.columns = expected_cols[:len(df.columns)]


# -------------------------
# Convert numeric column
# -------------------------
def tofloat(x):
    try:
        return float(x)
    except:
        return np.nan

df['val1'] = df['val1'].replace({'--': None, '': None})
df['val1f'] = df['val1'].apply(tofloat)


# -------------------------
# Map diseases to groups
# -------------------------
def disease_group(name):
    if pd.isna(name):
        return None
    s = name.lower()
    if 'stroke' in s or 'isles' in s:
        return 'Stroke'
    if 'tumour' in s or 'tumor' in s or 'brats' in s:
        return 'Tumour'
    if s.strip().startswith('ms') or ' ms' in s or 'multiple' in s:
        return 'MS'
    if 'wmh' in s:
        return 'WMH'
    return None

df['group'] = df['disease'].apply(disease_group)
df_plot = df[df['group'].notna()].copy()


# -------------------------
# Aggregate data
# -------------------------
categories = ['Diffusion', 'AE', 'VAE', 'GAN']
groups = ['Stroke', 'Tumour', 'MS', 'WMH']

agg = {}
for g in groups:
    sub = df_plot[df_plot['group'] == g]
    agg[g] = {}
    for cat in categories:
        vals = sub[sub['method'].str.upper().str.strip() == cat.upper()]['val1f'].dropna().values
        if len(vals) > 0:
            agg[g][cat] = {
                'vals': vals,
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals, ddof=1) if len(vals) > 1 else 0.0),
            }
        else:
            agg[g][cat] = None


# -------------------------
# Plotting
# -------------------------
plt.rcParams.update({'font.size': 10})
fig, axes = plt.subplots(2, 2, figsize=(8, 8))
axes = axes.flatten()

for ax, g in zip(axes, groups):
    data = agg[g]
    present = [c for c in categories if data[c] is not None]
    if not present:
        ax.set_visible(False)
        continue

    means = [data[c]['mean'] for c in present]
    stds = [data[c]['std'] for c in present]
    x = np.arange(len(present))

    # Bars with errorbars
    ax.bar(x, means, yerr=stds, capsize=5, color='skyblue', edgecolor='black')

    # Overlay datapoints with jitter
    for i, c in enumerate(present):
        vals = data[c]['vals']
        jitter = (np.random.rand(len(vals)) - 0.5) * 0.2
        ax.scatter(np.full_like(vals, x[i]) + jitter, vals, color='darkblue', alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(present)
    ax.set_title(g)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel('Primary metric (val1)')

fig.tight_layout()
plt.savefig("figure_grid.png", dpi=200)
plt.show()


# -------------------------
# Optional: summary table
# -------------------------
summary = []
for g in groups:
    for c in categories:
        entry = agg[g][c]
        if entry:
            summary.append({
                'Group': g,
                'Category': c,
                'N': len(entry['vals']),
                'Mean': entry['mean'],
                'SD': entry['std'],
            })

summary_df = pd.DataFrame(summary)
print("\nSummary (per group & category):")
print(summary_df.to_string(index=False))
