#!/usr/bin/env Rscript
#
# R Visualization Sub-Agent
#
# This autonomous sub-agent specializes in creating professional,
# publication-quality economic visualizations using ggplot2.
#
# Sub-Agent Responsibilities:
#   1. Load validated economic time series data
#   2. Create multi-panel visualization with three series:
#      - Real GDP growth
#      - Unemployment rate
#      - Federal funds rate
#   3. Apply professional styling and formatting
#   4. Add recession shading (NBER dates)
#   5. Export high-resolution PNG (300 DPI)
#
# Output:
#   - outputs/economic_dashboard.png: Multi-panel dashboard
#
# Author: Claude Code Demo - R Visualization Sub-Agent
# Date: 2025-10-15

# Required libraries
suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(scales)
  library(patchwork)
})

# Configuration
DATA_DIR <- "data/validated"
OUTPUT_DIR <- "outputs"
OUTPUT_FILE <- file.path(OUTPUT_DIR, "economic_dashboard.png")

# NBER recession dates (last 10 years for reference)
# Source: https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions
RECESSIONS <- data.frame(
  start = as.Date(c("2020-02-01")),
  end = as.Date(c("2020-04-30"))
)

#' Load and prepare economic time series data
#'
#' @param filename Name of CSV file in validated data directory
#' @param series_name Descriptive name for the series
#' @return Data frame with date, value, and series columns
load_series <- function(filename, series_name) {
  file_path <- file.path(DATA_DIR, filename)

  if (!file.exists(file_path)) {
    stop(paste("Data file not found:", file_path))
  }

  df <- read_csv(file_path, show_col_types = FALSE)
  df$series <- series_name

  return(df)
}

#' Create recession shading layer for ggplot
#'
#' @param recessions Data frame with start and end dates
#' @return ggplot2 geom_rect layer
add_recession_shading <- function(recessions) {
  if (nrow(recessions) == 0) {
    return(NULL)
  }

  geom_rect(
    data = recessions,
    aes(xmin = start, xmax = end, ymin = -Inf, ymax = Inf),
    fill = "gray70",
    alpha = 0.3,
    inherit.aes = FALSE
  )
}

#' Create styled panel for a single economic series
#'
#' @param data Data frame with date and value columns
#' @param title Panel title
#' @param y_label Y-axis label with units
#' @param color Line color
#' @return ggplot object
create_panel <- function(data, title, y_label, color = "#2C3E50") {
  p <- ggplot(data, aes(x = date, y = value)) +
    # Add recession shading in background
    add_recession_shading(RECESSIONS) +
    # Main time series line
    geom_line(color = color, linewidth = 1.0) +
    # Styling
    labs(
      title = title,
      x = NULL,
      y = y_label
    ) +
    scale_x_date(
      date_labels = "%Y",
      date_breaks = "1 year",
      expand = c(0.01, 0)
    ) +
    scale_y_continuous(
      labels = comma
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(face = "bold", size = 12),
      axis.title.y = element_text(size = 10, margin = margin(r = 10)),
      axis.text = element_text(size = 9),
      panel.grid.minor = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.major.y = element_line(color = "gray90"),
      plot.margin = margin(10, 10, 10, 10)
    )

  return(p)
}

#' Main visualization pipeline
#'
#' This function orchestrates the creation of the economic dashboard:
#' 1. Load validated data files
#' 2. Create individual panels for each series
#' 3. Combine into multi-panel layout
#' 4. Add overall title and source attribution
#' 5. Export high-resolution PNG
main <- function() {
  cat("\n=== R Visualization Sub-Agent ===\n\n")

  # Create output directory if needed
  dir.create(OUTPUT_DIR, showWarnings = FALSE, recursive = TRUE)

  # Load data
  cat("Loading validated data...\n")

  tryCatch({
    gdp_data <- load_series("gdp.csv", "GDP")
    unemp_data <- load_series("unemployment.csv", "Unemployment")
    fed_data <- load_series("fed_funds.csv", "Fed Funds")

    cat(sprintf("  - GDP: %d observations\n", nrow(gdp_data)))
    cat(sprintf("  - Unemployment: %d observations\n", nrow(unemp_data)))
    cat(sprintf("  - Fed Funds: %d observations\n", nrow(fed_data)))

  }, error = function(e) {
    cat(sprintf("ERROR: Failed to load data - %s\n", e$message))
    quit(status = 1)
  })

  # Create individual panels
  cat("\nCreating visualization panels...\n")

  p1 <- create_panel(
    gdp_data,
    title = "Real Gross Domestic Product (GDPC1)",
    y_label = "Billions of 2017 Dollars",
    color = "#27AE60"
  )

  p2 <- create_panel(
    unemp_data,
    title = "Unemployment Rate (UNRATE)",
    y_label = "Percent",
    color = "#E74C3C"
  )

  p3 <- create_panel(
    fed_data,
    title = "Federal Funds Effective Rate (DFF)",
    y_label = "Percent",
    color = "#3498DB"
  )

  # Combine panels using patchwork
  cat("Assembling multi-panel dashboard...\n")

  combined <- p1 / p2 / p3 +
    plot_annotation(
      title = "U.S. Economic Indicators: Last 5 Years",
      subtitle = "Quarterly data from Federal Reserve Economic Data (FRED)",
      caption = "Source: Federal Reserve Bank of St. Louis | Gray shading indicates NBER recession periods",
      theme = theme(
        plot.title = element_text(size = 16, face = "bold", hjust = 0),
        plot.subtitle = element_text(size = 11, color = "gray40", hjust = 0),
        plot.caption = element_text(size = 8, color = "gray50", hjust = 1)
      )
    )

  # Save high-resolution output
  cat(sprintf("Saving dashboard to: %s\n", OUTPUT_FILE))

  ggsave(
    filename = OUTPUT_FILE,
    plot = combined,
    width = 10,
    height = 12,
    dpi = 300,
    units = "in",
    bg = "white"
  )

  cat("\n✓ Visualization complete!\n\n")

  # Return success
  quit(status = 0)
}

# Execute main pipeline
if (!interactive()) {
  main()
}
