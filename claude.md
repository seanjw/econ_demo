# Economic Data Analysis: Sub-Agent Architecture Demo

## Overview

This project demonstrates a **sub-agent architecture** for economic data analysis using the Federal Reserve Economic Data (FRED) API and public opinion data from YouGov. It showcases how complex analytical workflows can be decomposed into specialized, autonomous agents that work together under the coordination of a main orchestrator.

**Academic Purpose**: This demo illustrates modern AI-assisted software engineering patterns where different analytical tasks (data collection, web scraping, validation, statistical analysis, visualization) are delegated to specialized sub-agents, each with domain-specific expertise.

## Architecture

### Main Orchestrator (`main.py`)
The primary agent responsible for:
- Fetching economic time series data from FRED API (with parallel processing)
- Coordinating all sub-agent execution
- Managing the overall workflow
- Handling errors and reporting results

**Economic Data Series Collected**:
- `GDPC1`: Real Gross Domestic Product (Quarterly)
- `UNRATE`: Unemployment Rate (Monthly, aggregated to quarterly)
- `DFF`: Federal Funds Effective Rate (Daily, aggregated to quarterly)

### Sub-Agent 1: Opinion Scraper (`agents/opinion_scraper.py`)

**Role**: Collects public opinion data about the U.S. economy

**Invocation**:
```python
python agents/opinion_scraper.py
```

**Responsibilities**:
1. **Web Scraping**: Fetch data from YouGov economy tracker
2. **Fallback Data Generation**: Create representative sample data if live scraping fails
3. **Frequency Aggregation**: Convert monthly data to quarterly to match economic indicators
4. **Data Structuring**: Format opinion metrics (getting better %, getting worse %, net sentiment)
5. **Metadata Tracking**: Record source URL, scrape date, and observation counts

**Output**:
- `data/raw/public_opinion.csv`: Quarterly opinion time series
- `outputs/opinion_metadata.json`: Scraping metadata

**Opinion Metrics**:
- `getting_better_pct`: Percentage who think economy is getting better
- `getting_worse_pct`: Percentage who think economy is getting worse
- `staying_same_pct`: Percentage who think economy is staying the same
- `net_sentiment`: Difference between "better" and "worse" percentages

**Note**: Opinion data collection is optional and non-fatal. The pipeline continues without it if unavailable.

### Sub-Agent 2: Data Validator (`agents/validator.py`)

**Role**: Ensures data quality and integrity before analysis

**Invocation**:
```python
python agents/validator.py
```

**Responsibilities**:
1. **Completeness Check**: Verify no missing dates in time series
2. **Format Validation**: Ensure dates follow ISO format (YYYY-MM-DD)
3. **Sequence Verification**: Confirm chronological ordering
4. **Range Validation**: Check values are economically reasonable:
   - GDP growth: -20% to +20% quarterly
   - Unemployment: 0% to 30%
   - Federal Funds Rate: 0% to 25%
5. **Alignment Check**: Verify all three series cover the same time periods

**Output**: `outputs/validation_report.json`
```json
{
  "timestamp": "2025-10-15T10:30:00",
  "status": "PASS" | "FAIL",
  "checks": {
    "completeness": {"passed": true, "issues": []},
    "format": {"passed": true, "issues": []},
    "ranges": {"passed": true, "issues": []},
    "alignment": {"passed": true, "issues": []}
  },
  "summary": "All validation checks passed"
}
```

### Sub-Agent 3: R Visualization Expert (`agents/plotter.R`)

**Role**: Creates professional publication-quality visualizations

**Invocation**:
```r
Rscript agents/plotter.R
```

**Responsibilities**:
1. Load validated CSV files from `data/validated/`
2. Create multi-panel ggplot2 visualization showing:
   - Real GDP (top panel)
   - Unemployment rate (middle panel)
   - Federal Funds Rate (bottom panel)
3. Add NBER recession shading where applicable
4. Apply professional styling with proper:
   - Axis labels with units
   - Titles and subtitles
   - Data source attribution
   - Consistent color scheme
5. Export high-resolution PNG (300 DPI)

**Output**: `outputs/economic_dashboard.png`

**R Dependencies**:
- `ggplot2`: Grammar of graphics plotting
- `dplyr`: Data manipulation
- `readr`: Fast CSV reading
- `scales`: Axis formatting
- `patchwork`: Multi-panel layouts

### Sub-Agent 4: Statistical Analyzer (`agents/analyzer.py`)

**Role**: Performs econometric analysis and generates LaTeX tables

**Invocation**:
```python
python agents/analyzer.py
```

**Responsibilities**:
1. **Correlation Analysis**: Compute Pearson correlations between economic indicators with significance tests
2. **Granger Causality Tests**: Test predictive relationships with up to 4 lags
3. **Descriptive Statistics**: Summary statistics for each economic series
4. **Opinion-Economy Analysis** (Extension): Test relationships between lagged economic indicators (quarter t-1) and public opinion (quarter t)
5. **LaTeX Table Generation**: Create publication-ready tables for all analyses

**Output**:
- `outputs/statistical_analysis.json`: Complete statistical results
- `outputs/correlation_matrix.tex`: LaTeX correlation table
- `outputs/granger_causality.tex`: LaTeX Granger test results
- `outputs/descriptive_stats.tex`: LaTeX descriptive statistics
- `outputs/opinion_economy.tex`: LaTeX opinion-economy correlations (if opinion data available)

**Key Statistical Methods**:
- Pearson correlation with t-tests for significance
- Granger causality F-tests (SSR method)
- Lagged correlation analysis (economic indicators at t-1 vs. opinion at t)
- Significance levels: 1%, 5%, 10%

**Python Dependencies**:
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `scipy`: Statistical tests
- `statsmodels`: Granger causality tests

### Sub-Agent 5: Report Generator (`agents/reporter.py`)

**Role**: Generates comprehensive PDF reports with narrative interpretation

**Invocation**:
```python
python agents/reporter.py
```

**Responsibilities**:
1. **Load Analysis Results**: Import all statistical outputs and visualizations
2. **Narrative Interpretation**: Auto-interpret correlations, Granger tests, and opinion-economy relationships
3. **Quarto Markdown Generation**: Create .qmd file with:
   - Executive summary
   - Data quality section
   - Descriptive statistics with interpretation
   - Time series visualization
   - Correlation analysis with markdown tables
   - Granger causality findings
   - Opinion-economy analysis (if available)
   - Methodology section
   - Data source citations
4. **PDF Compilation**: Use Quarto to compile markdown to professional PDF

**Output**:
- `outputs/economic_report.qmd`: Quarto Markdown source (version-controlled)
- `outputs/economic_report.pdf`: Compiled PDF report

**Quarto Dependency**:
- Install via: `brew install quarto` (macOS) or download from https://quarto.org

## Workflow Execution

### 7-Stage Pipeline

```
┌─────────────────────────────────────┐
│       Main Orchestrator             │
│         (main.py)                   │
└─────────────┬───────────────────────┘
              │
              ▼
    ┌───────────────────┐
    │  Stage 1:         │
    │  Fetch FRED Data  │
    │  (Parallel)       │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │  Stage 2:         │
    │  Opinion Scraper  │
    │  (Optional)       │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │  Stage 3:         │
    │  Data Validator   │
    └─────────┬─────────┘
              │
              ├─── FAIL ──→ Report & Exit
              │
              ▼ PASS
    ┌───────────────────┐
    │  Copy to          │
    │  validated/       │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │  Stage 4:         │
    │  R Visualization  │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │  Stage 5:         │
    │  Statistical      │
    │  Analyzer         │
    │  + Opinion Corr.  │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │  Stage 6:         │
    │  Report Generator │
    │  (QMD → PDF)      │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │  Stage 7:         │
    │  Pipeline Summary │
    └───────────────────┘
```

## Running the Demo

### Prerequisites

**Python Dependencies**:
```bash
pip install -r requirements.txt
```

**R Dependencies**:
```r
install.packages(c("ggplot2", "dplyr", "readr", "scales", "patchwork"))
```

**Quarto** (for PDF report generation):
```bash
# macOS
brew install quarto

# Or download from https://quarto.org
```

### Execution

```bash
# Run the complete pipeline
python3 main.py

# Or run sub-agents individually:
python3 agents/opinion_scraper.py
python3 agents/validator.py
Rscript agents/plotter.R
python3 agents/analyzer.py
python3 agents/reporter.py
```

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

## File Structure

```
econ_demo/
├── README.md                    # Quick start guide
├── claude.md                    # This comprehensive documentation
├── secrets.yaml                 # FRED API credentials
├── requirements.txt             # Python dependencies
├── main.py                      # Main orchestrator (7-stage pipeline)
│
├── agents/                      # Sub-agent modules
│   ├── opinion_scraper.py      # Public opinion scraper (Sub-Agent 1)
│   ├── validator.py            # Data validation (Sub-Agent 2)
│   ├── plotter.R               # R visualization (Sub-Agent 3)
│   ├── analyzer.py             # Statistical analysis (Sub-Agent 4)
│   └── reporter.py             # Report generation (Sub-Agent 5)
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

## Educational Highlights

### 1. Separation of Concerns
Each agent has a single, well-defined responsibility:
- Main agent: Data acquisition and orchestration
- Validator: Quality assurance
- Plotter: Visualization

### 2. Language Agnostic
Sub-agents can be written in different languages based on their strengths:
- Python for API integration and orchestration
- Python for data validation (pandas ecosystem)
- R for statistical visualization (ggplot2 excellence)

### 3. Testable Components
Each sub-agent can be:
- Tested independently
- Run in isolation for debugging
- Replaced with improved implementations
- Extended with new capabilities

### 4. Error Handling
The pipeline implements defensive programming:
- Validation gates prevent bad data from propagating
- Clear error messages guide troubleshooting
- Graceful failure with informative logs

### 5. Reproducibility
All analysis steps are:
- Version controlled
- Documented
- Automated
- Repeatable with a single command

### 6. Opinion-Economy Correlation Analysis

**Key Research Question**: Do economic conditions in one quarter predict public sentiment in the next quarter?

**Methodology**:
- Lag economic indicators by 1 quarter (t-1)
- Match with current quarter opinion data (t)
- Compute Pearson correlations with significance tests
- Use quarter-based matching to handle date format differences

**Example Findings** (from sample data):
- **Unemployment Rate (t-1) → Net Sentiment (t)**: r = 0.577*** (p < 0.01)
  - Higher unemployment in the prior quarter significantly predicts more negative public sentiment
- **Fed Funds Rate (t-1) → Getting Worse % (t)**: r = 0.219 (not significant)
- **Real GDP (t-1) → Net Sentiment (t)**: r = -0.027 (not significant)

**Interpretation**: The unemployment rate appears to be the economic indicator most strongly associated with subsequent changes in public opinion about the economy, suggesting that labor market conditions have a lagged impact on how the public perceives the economy's direction.

## Future Extension Ideas

For further academic exploration:

1. **Multi-lag Analysis**
   - Test opinion-economy relationships at 2, 3, and 4 quarter lags
   - Identify optimal lag structure for different indicators

2. **Vector Autoregression (VAR)**
   - Model bidirectional relationships between economics and opinion
   - Include impulse response functions

3. **Streaming Updates**
   - Monitor FRED for new data releases
   - Automatically re-scrape YouGov opinion data
   - Re-run pipeline and track changes over time

4. **Additional Opinion Sources**
   - Integrate multiple opinion polls (Gallup, Pew, etc.)
   - Sentiment analysis from news headlines or social media
   - Consumer confidence indices

## Questions and Support

This demo was created to showcase Claude Code's ability to architect complex, multi-agent systems. For questions about:
- **FRED API**: https://fred.stlouisfed.org/docs/api/
- **YouGov Data**: https://today.yougov.com
- **Sub-agent patterns**: See code comments in `main.py` and individual sub-agent files
- **Economic data**: Consult Federal Reserve documentation
- **Statistical methods**: See `agents/analyzer.py` for implementation details
- **Quarto Markdown**: https://quarto.org/docs/

## Key Technologies

- **Python 3**: Main orchestration, data processing, statistical analysis
- **R**: Statistical visualization with ggplot2
- **Quarto**: Reproducible document generation
- **FRED API**: Economic data source
- **BeautifulSoup**: Web scraping (with fallback to sample data)
- **pandas/numpy**: Data manipulation
- **scipy/statsmodels**: Statistical testing
- **Concurrent Futures**: Parallel API requests

## License

This is an academic demonstration project. FRED data is public domain (U.S. government data). YouGov data collection respects rate limits and includes fallback to representative sample data for demonstration purposes.
