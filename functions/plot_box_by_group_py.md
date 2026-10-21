---
id: plot_box_by_group_py
name: Grouped Sound Pressure Level Box Plot (Python)
description: Draws colored sound-pressure-level box plots by group and marks energy-equivalent means.
language: Python
execution_instructions: Requires numpy and matplotlib. Pass a label-to-values mapping and a matching label-to-color mapping.
required_fields:
  - sound_pressure_level
output_type: Figure/Plot
translation_status: ready
citation: "Adapted from the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```python
import numpy as np
import matplotlib.pyplot as plt


def energy_mean_db(values):
    """Return the energy-equivalent mean of sound levels in decibels."""
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    if values.size == 0:
        return np.nan
    return 10.0 * np.log10(np.mean(np.power(10.0, values / 10.0)))


def plot_box_by_group(
    data_dict,
    colors,
    xlabel,
    ylabel,
    title,
    ax=None,
    figsize=(8, 5),
    rotate_xticks=True,
    energy_mean=True,
):
    """Draw colored box plots and optional energy-equivalent mean markers."""
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    labels = list(data_dict)
    data = [data_dict[label] for label in labels]
    tick_labels = [f"{label}\n(n={len(values):,})" for label, values in zip(labels, data)]
    boxplot = ax.boxplot(
        data, labels=tick_labels, showmeans=not energy_mean, patch_artist=True
    )
    if energy_mean:
        ax.scatter(
            range(1, len(data) + 1),
            [energy_mean_db(values) for values in data],
            marker="^",
            color="green",
            s=30,
            zorder=3,
        )
    for patch, label in zip(boxplot["boxes"], labels):
        patch.set_facecolor(colors[label])
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if rotate_xticks:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    return ax
```
