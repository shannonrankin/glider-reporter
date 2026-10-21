---
id: plot_corr_matrix_r
name: Ocean Variable Correlation Matrix (R)
description: Draws an annotated Pearson correlation heatmap for selected oceanographic variables.
language: R
execution_instructions: Requires ggplot2 and tidyr. Pass a data frame and selected numeric column names.
required_fields:
  - temperature
  - salinity
  - depth
output_type: Figure/Plot
translation_status: ready
citation: "R translation of the PAM-Glider Noise Profiler plotting utilities: https://github.com/jeengdahl97/noise-fx-calc/blob/c2334e4dfcb66604dfa958d8aee554752f8f1b4e/noise_utils.py"
issue_url: https://github.com/shannonrankin/glider-reporter/issues/38
---

## Code

```r
plot_corr_matrix <- function(data, variables, title) {
  complete_data <- stats::na.omit(data[, variables, drop = FALSE])
  matrix <- stats::cor(complete_data, method = "pearson")
  plot_data <- as.data.frame(as.table(matrix))
  names(plot_data) <- c("variable_x", "variable_y", "correlation")

  ggplot2::ggplot(
    plot_data,
    ggplot2::aes(x = variable_x, y = variable_y, fill = correlation)
  ) +
    ggplot2::geom_tile() +
    ggplot2::geom_text(
      ggplot2::aes(label = sprintf("%.2f", correlation)),
      size = 3
    ) +
    ggplot2::scale_fill_gradient2(
      low = "#2166AC",
      mid = "white",
      high = "#B2182B",
      midpoint = 0,
      limits = c(-1, 1)
    ) +
    ggplot2::labs(title = title, x = NULL, y = NULL, fill = "Correlation") +
    ggplot2::theme_minimal()
}
```
