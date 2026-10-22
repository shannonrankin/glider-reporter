---
id: plot_corr_matrix_py
name: Ocean Variable Correlation Matrix (Python)
description: Draws an annotated Pearson correlation heatmap for selected oceanographic variables.
language: Python
execution_instructions: Requires pandas, seaborn, and matplotlib. Pass a pandas DataFrame, selected numeric column names, a title, and a matplotlib axis.
required_fields:
  - temperature
  - salinity
  - depth
output_type: Figure/Plot
translation_status: ready
citation: "Adapted from the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```python
import seaborn as sns


def plot_corr_matrix(df, variables, title, ax, cbar=True, annot_kws=None):
    """Draw and return the complete-case Pearson correlation matrix."""
    matrix = df[variables].dropna().corr()
    sns.heatmap(
        matrix,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        ax=ax,
        cbar=cbar,
        annot_kws=annot_kws,
    )
    ax.set_title(title)
    return matrix
```
