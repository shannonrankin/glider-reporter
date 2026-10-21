---
id: setup_map_axes_r
name: Glider Track Map Axes (R)
description: Creates a ggplot map backdrop with coastlines and geographic coordinates for plotting glider tracks.
language: R
execution_instructions: Requires ggplot2 and maps. Add ggplot2::geom_path() with longitude and latitude columns to the returned plot.
required_fields:
  - latitude
  - longitude
output_type: Figure/Plot
translation_status: ready
citation: "R translation of the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```r
setup_map_axes <- function(extent, left_labels = TRUE) {
  coastline <- maps::map_data("world")

  ggplot2::ggplot() +
    ggplot2::geom_polygon(
      data = coastline,
      ggplot2::aes(x = long, y = lat, group = group),
      fill = "lightgray",
      color = "gray50",
      linewidth = 0.2
    ) +
    ggplot2::coord_quickmap(
      xlim = extent[c(1, 2)],
      ylim = extent[c(3, 4)],
      expand = FALSE
    ) +
    ggplot2::labs(
      x = "Longitude (decimal degrees)",
      y = if (left_labels) "Latitude (decimal degrees)" else NULL
    ) +
    ggplot2::theme_minimal()
}
```
