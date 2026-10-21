---
id: plot_box_by_group_r
name: Grouped Sound Pressure Level Box Plot (R)
description: Draws sound-pressure-level box plots by group and marks energy-equivalent means.
language: R
execution_instructions: Requires dplyr and ggplot2. Pass a data frame with sound_pressure_level and a grouping column.
required_fields:
  - sound_pressure_level
output_type: Figure/Plot
translation_status: ready
citation: "R translation of the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```r
energy_mean_db <- function(values) {
  values <- values[!is.na(values)]
  if (length(values) == 0) {
    return(NaN)
  }
  10 * log10(mean(10^(values / 10)))
}

plot_box_by_group <- function(data, group_column, title) {
  group_means <- data |>
    dplyr::group_by(.data[[group_column]]) |>
    dplyr::summarise(
      energy_mean = energy_mean_db(sound_pressure_level),
      .groups = "drop"
    )

  ggplot2::ggplot(
    data,
    ggplot2::aes(
      x = .data[[group_column]],
      y = sound_pressure_level,
      fill = .data[[group_column]]
    )
  ) +
    ggplot2::geom_boxplot() +
    ggplot2::geom_point(
      data = group_means,
      ggplot2::aes(
        x = .data[[group_column]],
        y = energy_mean
      ),
      shape = 17,
      color = "green",
      size = 3,
      inherit.aes = FALSE
    ) +
    ggplot2::labs(
      title = title,
      x = group_column,
      y = "SPL (dB re: 1 μPa)"
    ) +
    ggplot2::theme_minimal() +
    ggplot2::theme(legend.position = "none")
}
```
