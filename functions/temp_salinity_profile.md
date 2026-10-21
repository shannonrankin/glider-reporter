---
id: temp_salinity_profile
name: Temperature & Salinity Depth Profile
description: Plots vertical depth profiles of temperature and salinity across the glider mission.
language: R
execution_instructions: Requires R with readr, here, and ggplot2. Run from the repository root.
required_fields:
  - depth
  - temperature
  - salinity
output_type: Figure/Plot
translation_status: ready
citation: OceanGliders Quality Control Manual v1.0
issue_url: https://github.com/shannonrankin/glider-reporter/issues/2
---

## Code

```r
profile_data <- readr::read_csv(
  here::here("data", "sample", "og10_standard", "glider_og10_data.csv"),
  show_col_types = FALSE
)

plot_data <- base::rbind(
  data.frame(
    depth = profile_data$depth,
    value = profile_data$temperature,
    measurement = "Temperature (°C)"
  ),
  data.frame(
    depth = profile_data$depth,
    value = profile_data$salinity,
    measurement = "Salinity (PSU)"
  )
)

profile_plot <- ggplot2::ggplot(
  plot_data,
  ggplot2::aes(x = value, y = depth)
) +
  ggplot2::geom_path(linewidth = 0.7, color = "#0072B2") +
  ggplot2::scale_y_reverse() +
  ggplot2::facet_wrap(
    ggplot2::vars(measurement),
    scales = "free_x",
    nrow = 1
  ) +
  ggplot2::labs(
    title = "Temperature and Salinity Depth Profiles",
    x = NULL,
    y = "Depth (m)"
  ) +
  ggplot2::theme_minimal()

ggplot2::ggsave(
  here::here("data", "precomputed_outputs", "temp_salinity_profile.png"),
  plot = profile_plot,
  width = 8,
  height = 5,
  dpi = 150
)

profile_plot
```
