# Economic Data Analysis: Sub-Agent Architecture Demo (Extended)

This project demonstrates a production-ready sub-agent architecture for economic data analysis, built for academic demonstration to an economics department. This extended version includes advanced statistical analysis, public opinion-economy correlation analysis, automated report generation, and parallel processing capabilities.

## Quick Start

### Prerequisites

**Python Dependencies:**
```bash
pip install -r requirements.txt
```

**R Dependencies:**
```r
install.packages(c("ggplot2", "dplyr", "readr", "scales", "patchwork"))
```

**Quarto (for PDF report generation):**
```bash
# macOS
brew install quarto

# Or download from https://quarto.org/docs/get-started/
```

### Run the Complete Pipeline

```bash
python3 main.py
```

This single command will:
1. Fetch 5 years of economic data from FRED (GDP, Unemployment, Fed Funds Rate) **in parallel**
2. **Scrape public opinion data from YouGov economy tracker (with sample data fallback)**
3. Validate data quality using the validation sub-agent
4. Generate a professional visualization using the R plotting sub-agent
5. **Perform statistical analysis (correlations, Granger causality, opinion-economy relationships)**
6. **Generate a comprehensive PDF report with narrative interpretation**

### Expected Output

```
=== Economic Data Analysis Pipeline ===

[1/7] Fetching FRED data (parallel processing)...
  ✓ GDPC1 (Real GDP): 19 observations
  ✓ UNRATE (Unemployment Rate): 20 observations
  ✓ DFF (Federal Funds Rate): 21 observations

[2/7] Running opinion scraper sub-agent...
  ✓ Opinion data collected: data/raw/public_opinion.csv

[3/7] Running validation sub-agent...
  ✓ Data validation passed

[4/7] Running visualization sub-agent...
  ✓ Dashboard created: outputs/economic_dashboard.png

[5/7] Running statistical analysis sub-agent...
  ✓ Statistical analysis completed
    - JSON results: outputs/statistical_analysis.json
    - LaTeX tables: correlation_matrix.tex, granger_causality.tex,
                    descriptive_stats.tex, opinion_economy.tex

[6/7] Running report generation sub-agent...
  ✓ PDF report generated: outputs/economic_report.pdf

[7/7] Pipeline Summary

============================================================
✅ Complete Pipeline Executed Successfully!
============================================================

📊 Generated Outputs:
  1. Validation Report
  2. Economic Dashboard
  3. Statistical Analysis (JSON + LaTeX)
  4. Opinion-Economy Correlations
  5. Quarto Report (QMD)
  6. PDF Report

📁 Data Files:
  - Real GDP
  - Unemployment Rate
  - Federal Funds Rate
  - Public Opinion

🎯 Key Features Demonstrated:
  ✓ Parallel data fetching
  ✓ Statistical analysis with Granger causality
  ✓ Opinion-economy correlation analysis with lagged indicators
  ✓ Automated PDF report generation
  ✓ Multi-language integration (Python + R)
  ✓ Web scraping with fallback to sample data
  ✓ Sub-agent architecture with 6 specialized agents
```

## Project Structure

```
econ_demo/
├── README.md                    # This file
├── claude.md                    # Detailed documentation
├── secrets.yaml                 # FRED API credentials
├── requirements.txt             # Python dependencies
├── main.py                      # Main orchestrator (7-stage pipeline with parallel processing)
│
├── agents/                      # Sub-agent modules
│   ├── opinion_scraper.py      # Public opinion scraper (Sub-Agent 1)
│   ├── validator.py            # Data validation (Sub-Agent 2)
│   ├── plotter.R               # R visualization (Sub-Agent 3)
│   ├── analyzer.py             # Statistical analysis with opinion correlations (Sub-Agent 4)
│   └── reporter.py             # PDF report generator (Sub-Agent 5)
│
├── data/
│   ├── raw/                    # Raw data from APIs
│   │   ├── gdp.csv
│   │   ├── unemployment.csv
│   │   ├── fed_funds.csv
│   │   └── public_opinion.csv  # YouGov opinion data (optional)
│   └── validated/              # Post-validation economic data
│       ├── gdp.csv
│       ├── unemployment.csv
│       └── fed_funds.csv
│
└── outputs/
    ├── validation_report.json       # Data quality report
    ├── economic_dashboard.png       # Multi-panel visualization
    ├── statistical_analysis.json    # Complete statistical results
    ├── correlation_matrix.tex       # LaTeX correlation table
    ├── granger_causality.tex        # LaTeX Granger tests
    ├── descriptive_stats.tex        # LaTeX descriptive stats
    ├── opinion_economy.tex          # LaTeX opinion-economy correlations
    ├── opinion_metadata.json        # Opinion scraping metadata
    ├── economic_report.qmd          # Quarto Markdown source
    └── economic_report.pdf          # Final PDF report
```

## Sub-Agent Architecture

### Main Orchestrator (`main.py`)
- Fetches economic data from FRED API **with parallel processing**
- Coordinates all sub-agent execution
- Manages workflow and error handling
- Runs 7-stage pipeline from data collection to final report

### Sub-Agent 1: Opinion Scraper (`agents/opinion_scraper.py`)
- Scrapes public opinion data from YouGov economy tracker
- Generates representative sample data as fallback
- Aggregates to quarterly frequency
- Outputs CSV with opinion metrics (getting better %, getting worse %, net sentiment)
- Non-fatal if unavailable (pipeline continues)

### Sub-Agent 2: Data Validator (`agents/validator.py`)
- Checks data completeness and format
- Validates economically reasonable ranges
- Ensures series alignment
- Outputs JSON validation report

### Sub-Agent 3: R Visualization Expert (`agents/plotter.R`)
- Creates multi-panel ggplot2 visualization
- Adds professional styling and recession shading
- Exports high-resolution PNG (300 DPI)

### Sub-Agent 4: Statistical Analyzer (`agents/analyzer.py`)
- Computes correlation matrices with significance tests
- Performs Granger causality tests (up to 4 lags)
- **Analyzes opinion-economy relationships with lagged indicators**
- Generates descriptive statistics
- Outputs LaTeX tables for academic publications
- Creates JSON file with complete statistical results

### Sub-Agent 5: Report Generator (`agents/reporter.py`)
- Generates Quarto Markdown (.qmd) with narrative interpretation
- Auto-interprets economic relationships and statistical findings
- **Includes opinion-economy analysis section (if data available)**
- Combines visualizations, tables, and narrative text
- Compiles to publication-ready PDF using Quarto
- Ensures reproducible, version-controlled report generation

## Key Features

**Separation of Concerns**: Each agent has a single, well-defined responsibility

**Language Agnostic**: Python for data collection/validation, R for visualization

**Defensive Programming**: Validation gates prevent bad data from propagating

**Production Ready**: Comprehensive error handling and logging

**Reproducible**: All steps are automated and version controlled

## Running Sub-Agents Independently

Each sub-agent can be tested in isolation:

```bash
# Scrape opinion data
python3 agents/opinion_scraper.py

# After data collection, run validator alone
python3 agents/validator.py

# After validation, run plotter alone
Rscript agents/plotter.R

# Run statistical analysis alone (requires validated data, optional opinion data)
python3 agents/analyzer.py

# Generate PDF report alone (requires all previous outputs)
python3 agents/reporter.py
```

## Documentation

For comprehensive documentation on the sub-agent architecture, see **claude.md**.

## Academic Use

This project is designed to demonstrate:
- Modern AI-assisted software engineering patterns
- **Multi-agent system architecture with 6 specialized agents**
- Defensive programming practices
- Cross-language integration (Python + R)
- Economic data analysis workflows
- **Parallel processing for API data fetching**
- **Web scraping with robust error handling and fallback mechanisms**
- **Econometric analysis (correlations, Granger causality, lagged opinion-economy relationships)**
- **Automated narrative interpretation of statistical results**
- **Publication-ready LaTeX table generation**
- **Reproducible PDF report generation with Quarto Markdown**

Perfect for teaching:
- Software engineering concepts to economics graduate students or faculty
- Advanced Python programming (concurrent processing, web scraping, statistical analysis, Quarto integration)
- Econometric methodology implementation
- **Public opinion and economic data integration**
- **Lagged correlation analysis for predictive relationships**
- Research workflow automation
- Reproducible research practices with Quarto Markdown

### Example Research Question

**Do economic conditions in one quarter predict public sentiment in the next quarter?**

The pipeline automatically tests this by:
1. Collecting quarterly economic indicators (GDP, unemployment, Fed funds rate)
2. Collecting quarterly public opinion data (YouGov economy tracker)
3. Lagging economic indicators by 1 quarter
4. Computing correlations between lagged economics (t-1) and current opinion (t)
5. Generating LaTeX tables and narrative interpretation

**Sample Finding**: Unemployment rate in quarter t-1 significantly predicts net economic sentiment in quarter t (r = 0.577, p < 0.01), suggesting that labor market conditions have a lagged impact on public perception.

## Data Sources

**Economic Data** - Federal Reserve Economic Data (FRED) API:
- **GDPC1**: Real Gross Domestic Product
- **UNRATE**: Unemployment Rate
- **DFF**: Federal Funds Effective Rate

Source: Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org)

**Public Opinion Data** - YouGov Economy Tracker:
- Public perceptions of whether the economy is getting better, worse, or staying the same
- Aggregated to quarterly frequency
- Includes fallback to representative sample data for demonstration purposes

Source: YouGov (https://today.yougov.com/topics/economy/trackers/state-of-us-economy)

## License

This is an academic demonstration project. FRED data is public domain (U.S. government data). YouGov data collection respects rate limits and includes fallback to representative sample data for demonstration purposes.
