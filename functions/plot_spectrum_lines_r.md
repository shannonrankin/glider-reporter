---
id: plot_spectrum_lines_r
name: Grouped Acoustic Spectrum (R)
description: Plots one sound-pressure-level spectrum per group against logarithmic frequency.
language: R
execution_instructions: Requires ggplot2. Pass a data frame with frequency, sound_pressure_level, and grouping columns.
required_fields:
  - frequency
  - sound_pressure_level
output_type: Figure/Plot
translation_status: ready
citation: "R translation of the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```r
plot_spectrum_lines <- function(data, group_column, title) {
  ggplot2::ggplot(
    data,
    ggplot2::aes(
      x = frequency,
      y = sound_pressure_level,
      color = .data[[group_column]],
      group = .data[[group_column]]
    )
  ) +
    ggplot2::geom_line(linewidth = 0.7) +
    ggplot2::scale_x_log10() +
    ggplot2::labs(
      title = title,
      x = "Frequency (Hz)",
      y = "SPL (dB re: 1 μPa)",
      color = group_column
    ) +
    ggplot2::theme_minimal() +
    ggplot2::theme(legend.position = "bottom")
}
```
