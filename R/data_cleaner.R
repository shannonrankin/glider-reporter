# Utilities for normalising glider data to OG1.0-compatible values.

snake_case <- function(names) {
  names <- gsub("([a-z0-9])([A-Z])", "\\1_\\2", names, perl = TRUE)
  names <- gsub("[^A-Za-z0-9]+", "_", names)
  names <- tolower(gsub("^_|_$", "", names))
  names[names == ""] <- "unnamed"
  names
}

clean_glider_data <- function(df) {
  if (!is.data.frame(df)) {
    stop("df must be a data.frame")
  }

  names(df) <- snake_case(names(df))
  validation_errors <- character()
  validation_warnings <- character()

  aliases <- list(
    latitude = c("latitude", "lat", "lat_deg", "latitude_deg"),
    longitude = c("longitude", "lon", "lon_deg", "longitude_deg"),
    time = c("time", "iso_time", "timestamp")
  )
  essential_columns <- names(aliases)
  present_columns <- vapply(aliases, function(options) {
    any(options %in% names(df))
  }, logical(1))
  missing_columns <- essential_columns[!present_columns]
  if (length(missing_columns) > 0) {
    validation_errors <- paste("missing essential column:", missing_columns)
  }

  coordinate_columns <- vapply(aliases[c("latitude", "longitude")], function(options) {
    options[options %in% names(df)][1]
  }, character(1))
  for (column in coordinate_columns[!is.na(coordinate_columns)]) {
    values <- suppressWarnings(as.numeric(df[[column]]))
    values[!is.finite(values) | values < if (column == "latitude") -90 else -180 |
      values > if (column == "latitude") 90 else 180] <- NA_real_
    df[[column]] <- values
    if (anyNA(values)) {
      validation_warnings <- c(
        validation_warnings,
        paste(column, "contains missing or malformed values")
      )
    }
  }

  time_column <- aliases$time[aliases$time %in% names(df)][1]
  if (!is.na(time_column)) {
    parsed_time <- as.POSIXct(df[[time_column]], format = "%Y-%m-%dT%H:%M:%S", tz = "UTC")
    parsed_time[is.na(parsed_time)] <- as.POSIXct(
      df[[time_column]][is.na(parsed_time)], tz = "UTC"
    )
    df[[time_column]] <- ifelse(
      is.na(parsed_time),
      NA_character_,
      format(parsed_time, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
    )
    if (anyNA(parsed_time)) {
      validation_warnings <- c(
        validation_warnings,
        "time contains missing or malformed values"
      )
    }
  }

  attr(df, "validation") <- list(
    valid = length(validation_errors) == 0 && length(validation_warnings) == 0,
    errors = validation_errors,
    warnings = validation_warnings
  )
  df
}
