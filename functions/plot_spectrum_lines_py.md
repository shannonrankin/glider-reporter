---
id: plot_spectrum_lines_py
name: Grouped Acoustic Spectrum (Python)
description: Plots one sound-pressure-level spectrum per group against logarithmic frequency.
language: Python
execution_instructions: Requires matplotlib. Pass aligned frequency values in Hz, a label-to-SPL mapping, and a matching label-to-color mapping.
required_fields:
  - frequency
  - sound_pressure_level
output_type: Figure/Plot
translation_status: ready
citation: "Adapted from the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```python
import matplotlib.pyplot as plt


def plot_spectrum_lines(
    freqs,
    groups,
    colors,
    title,
    ax=None,
    figsize=(8, 5),
    legend_ncol=4,
    legend_fontsize=7,
    legend_anchor=-0.18,
):
    """Plot grouped SPL spectra with a logarithmic frequency axis."""
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    for label, values in groups.items():
        ax.plot(freqs, values, color=colors[label], label=str(label), linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("SPL (dB re: 1 μPa)")
    ax.set_title(title)
    ax.legend(
        fontsize=legend_fontsize,
        loc="upper center",
        bbox_to_anchor=(0.5, legend_anchor),
        ncol=legend_ncol,
    )
    return ax
```
