# Original Prompt (Opus)

I'm an academic preparing a demo for an economics department on how to use Claude Code.
In the session, I want to demonstrate how to: 1) use claude.md for project orchestration; 2) Employ sub-agents for specific tasks.

The demo will involve:
- Retrieving data from the FRED API (python)
- Scraping public opinion data from YouGov's "State of the U.S. Economy" tracker (python).
- Using separate sub-agents to:
    - Fetch FRED data (in parallel)
	- Collect and process YouGov data.
	- Validate all data for completeness
	- Using the downloaded data create plots (ggplot and R)
    - Generate a Quarto (QMD) report combining all outputs along with a narrative interpretation

Ask me questions before you start.

# Model questions

Great project! I'd be happy to help you create this economics demo for Claude Code. Before I start building the demo materials, I have a few questions to ensure I create exactly what you need:
Data & API Questions:

1. FRED API: Do you have a FRED API key already, or should the demo include obtaining one? Also, which specific economic indicators would you like to demonstrate pulling (e.g., GDP, unemployment rate, inflation metrics, interest rates)?

2. YouGov Data: Which specific metrics from the "State of the U.S. Economy" tracker are most relevant for your demo? (e.g., consumer confidence, economic outlook, inflation expectations)
Time Period: What date range should the demo cover for both data sources? Last year, last 5 years, or since COVID?

4. R Setup: Can I assume R and common packages (tidyverse, ggplot2, quarto) are already installed, or should the demo include setup instructions?

5. Python packages: Any preference for web scraping libraries (BeautifulSoup, Selenium, Playwright)?

6. Audience Level: Is this for faculty/grad students familiar with programming, or should it be accessible to those newer to these tools?

7. Narrative Focus: Any specific economic story you'd like the final report to tell? (e.g., comparing official statistics with public sentiment, inflation perceptions vs. reality)

8. Sub-agent Complexity: How sophisticated should the sub-agent orchestration be? Should it demonstrate error handling, retry logic, or keep it simple for clarity?

These details will help me create a demo that hits the right level of complexity and focuses on the most relevant aspects for your department.

# Responses

1. [xxxx]. GDP, Unemployment, fed funds rate. 
2. State of the US economy
3. 2020-present
4. Yes.
5. BeautifulSoup
6. They are smarter than me
7. Wing it.
8. Keep it simple

Now give me a final prompt 

# Final prompt (Sonnet)

# Economic Data Analysis Demo: FRED vs Public Sentiment (2020-Present)

Create a project demonstrating Claude Code's sub-agent architecture for economic research.

## Architecture Overview

### Main Orchestrator (`main.py`)
Create a 7-stage pipeline that:
1. Fetches FRED economic data in parallel (GDP, unemployment, fed funds rate)
2. Runs opinion scraper sub-agent (optional, non-fatal)
3. Runs validation sub-agent
4. Copies validated data to validated/ directory
5. Runs R visualization sub-agent
6. Runs statistical analysis sub-agent
7. Runs report generation sub-agent

Use concurrent.futures for parallel FRED API calls. Aggregate all data to quarterly frequency.

## Sub-Agents (5 Total)

### Sub-Agent 1: Opinion Scraper (`agents/opinion_scraper.py`)
- Scrape YouGov "State of the U.S. Economy" tracker using BeautifulSoup
- URL: https://today.yougov.com/topics/economy/trackers/state-of-the-us-economy
- Fallback to representative sample data if scraping fails
- Aggregate to quarterly frequency
- Extract: getting_better_pct, getting_worse_pct, staying_same_pct, net_sentiment
- Save to: data/raw/public_opinion.csv
- Generate: outputs/opinion_metadata.json

### Sub-Agent 2: Data Validator (`agents/validator.py`)
- Validate completeness (no missing quarters)
- Check date format (ISO YYYY-MM-DD)
- Verify chronological ordering
- Test economic ranges (GDP: -20% to +20%, unemployment: 0-30%, fed funds: 0-25%)
- Verify alignment across all three series
- Output: outputs/validation_report.json with PASS/FAIL status

### Sub-Agent 3: R Visualization Expert (`agents/plotter.R`)
- Load validated CSVs from data/validated/
- Create multi-panel ggplot2 dashboard:
  - Top: Real GDP time series
  - Middle: Unemployment rate
  - Bottom: Federal Funds Rate
- Apply professional styling with theme_minimal()
- Add proper axis labels, titles, data source attribution
- Export: outputs/economic_dashboard.png (300 DPI)
- Dependencies: ggplot2, dplyr, readr, scales, patchwork

### Sub-Agent 4: Statistical Analyzer (`agents/analyzer.py`)
- Compute Pearson correlations between all economic indicators with significance tests
- Run Granger causality tests (up to 4 lags) using statsmodels
- Calculate descriptive statistics for each series
- **Opinion-Economy Analysis**: Test lagged relationships (economic indicators at t-1 vs opinion at t)
- Generate LaTeX tables for all analyses
- Output:
  - outputs/statistical_analysis.json
  - outputs/correlation_matrix.tex
  - outputs/granger_causality.tex
  - outputs/descriptive_stats.tex
  - outputs/opinion_economy.tex
- Dependencies: pandas, numpy, scipy, statsmodels

### Sub-Agent 5: Report Generator (`agents/reporter.py`)
- Load all statistical results and visualizations
- Generate Quarto markdown (.qmd) with:
  - Executive summary
  - Data quality section
  - Descriptive statistics with auto-interpretation
  - Embedded time series visualization
  - Correlation analysis (markdown tables)
  - Granger causality findings
  - Opinion-economy analysis (if available)
  - Methodology section
  - Data source citations
- Compile to PDF using Quarto CLI
- Output:
  - outputs/economic_report.qmd
  - outputs/economic_report.pdf

## Key Requirements

### CLAUDE.md Documentation
Create comprehensive documentation showing:
- Complete 7-stage pipeline workflow diagram
- Individual sub-agent responsibilities
- Input/output specifications for each agent
- Opinion-economy correlation methodology
- Expected pipeline output with emojis and progress indicators
- File structure diagram
- Educational highlights (separation of concerns, language agnostic, testability)

### Data Structure
```
econ_demo/
├── CLAUDE.md (comprehensive docs)
├── main.py (7-stage orchestrator)
├── secrets.yaml (FRED API key)
├── requirements.txt
├── agents/
│   ├── opinion_scraper.py
│   ├── validator.py
│   ├── plotter.R
│   ├── analyzer.py
│   └── reporter.py
├── data/
│   ├── raw/ (GDP, unemployment, fed funds, opinion)
│   └── validated/ (post-validation economic data only)
└── outputs/
    ├── validation_report.json
    ├── economic_dashboard.png
    ├── statistical_analysis.json
    ├── *.tex (LaTeX tables)
    ├── opinion_metadata.json
    ├── economic_report.qmd
    └── economic_report.pdf
```

### Academic Features
- Reproducible research pipeline
- Multi-language integration (Python + R)
- Parallel data fetching
- Optional opinion data (non-fatal failures)
- Lagged correlation analysis (t-1 predictors)
- Professional LaTeX table formatting
- Automated PDF report generation with Quarto
- Clear separation of concerns across 5 specialized agents

Focus on clean, well-documented code suitable for teaching sub-agent architecture patterns.