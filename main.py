#!/usr/bin/env python3
"""
Economic Data Analysis Pipeline - Main Orchestrator

This script demonstrates a sub-agent architecture for economic data analysis.
It coordinates data collection from FRED API and delegates validation,
visualization, statistical analysis, and reporting tasks to specialized sub-agents.

Architecture:
    1. Main Agent (this script): Data collection and orchestration
    2. Opinion Scraper Sub-Agent: Public opinion data from YouGov
    3. Validator Sub-Agent: Data quality checks
    4. R Visualization Sub-Agent: Professional plotting
    5. Statistical Analyzer Sub-Agent: Correlations, Granger causality, opinion analysis, LaTeX tables
    6. Report Generator Sub-Agent: Quarto Markdown and PDF compilation

Features:
    - Parallel data fetching for improved performance
    - Defensive programming with validation gates
    - Multi-language integration (Python + R)
    - Publication-ready outputs

Author: Claude Code Demo
Date: 2025-10-15
"""

import os
import sys
import json
import yaml
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd


# Configuration
BASE_DIR = Path(__file__).parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_VALIDATED_DIR = BASE_DIR / "data" / "validated"
OUTPUTS_DIR = BASE_DIR / "outputs"
SECRETS_FILE = BASE_DIR / "secrets.yaml"

# Economic series to fetch from FRED
SERIES_CONFIG = {
    "gdp": {
        "series_id": "GDPC1",
        "name": "Real GDP",
        "frequency": "q",  # quarterly
        "filename": "gdp.csv"
    },
    "unemployment": {
        "series_id": "UNRATE",
        "name": "Unemployment Rate",
        "frequency": "m",  # monthly, will aggregate to quarterly
        "filename": "unemployment.csv"
    },
    "fed_funds": {
        "series_id": "DFF",
        "name": "Federal Funds Rate",
        "frequency": "d",  # daily, will aggregate to quarterly
        "filename": "fed_funds.csv"
    }
}


class FREDDataCollector:
    """
    Main agent for collecting economic data from FRED API.

    This agent is responsible for:
    - Loading API credentials
    - Fetching time series data
    - Converting to consistent quarterly frequency
    - Saving raw data for sub-agent processing
    """

    def __init__(self, api_key: str):
        """Initialize FRED data collector with API credentials."""
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.session = requests.Session()

    def fetch_series(
        self,
        series_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch a single time series from FRED API.

        Args:
            series_id: FRED series identifier (e.g., 'GDPC1')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with 'date' and 'value' columns

        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = f"{self.base_url}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date
        }

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()

        data = response.json()

        if "observations" not in data:
            raise ValueError(f"No observations returned for {series_id}")

        # Convert to DataFrame
        df = pd.DataFrame(data["observations"])
        df = df[["date", "value"]]

        # Handle missing values (marked as '.')
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()

        df["date"] = pd.to_datetime(df["date"])

        return df

    def aggregate_to_quarterly(
        self,
        df: pd.DataFrame,
        method: str = "mean"
    ) -> pd.DataFrame:
        """
        Aggregate time series data to quarterly frequency.

        Args:
            df: DataFrame with 'date' and 'value' columns
            method: Aggregation method ('mean' or 'last')

        Returns:
            Quarterly aggregated DataFrame
        """
        df = df.set_index("date")

        if method == "mean":
            quarterly = df.resample("QE").mean()
        elif method == "last":
            quarterly = df.resample("QE").last()
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

        quarterly = quarterly.reset_index()
        quarterly = quarterly.dropna()

        return quarterly

    def fetch_and_save(
        self,
        series_config: Dict,
        start_date: str,
        end_date: str,
        output_path: Path
    ) -> int:
        """
        Fetch a series and save to CSV.

        Args:
            series_config: Configuration dict with series_id, frequency, etc.
            start_date: Start date for data collection
            end_date: End date for data collection
            output_path: Path to save CSV file

        Returns:
            Number of observations collected
        """
        series_id = series_config["series_id"]
        frequency = series_config["frequency"]

        # Fetch raw data
        df = self.fetch_series(series_id, start_date, end_date)

        # Aggregate to quarterly if needed
        if frequency != "q":
            df = self.aggregate_to_quarterly(df, method="mean")

        # Save to CSV
        df.to_csv(output_path, index=False)

        return len(df)


def load_api_key() -> str:
    """
    Load FRED API key from secrets.yaml.

    Returns:
        API key string

    Raises:
        FileNotFoundError: If secrets.yaml not found
        KeyError: If API key not in secrets file
    """
    if not SECRETS_FILE.exists():
        raise FileNotFoundError(
            f"secrets.yaml not found at {SECRETS_FILE}. "
            "Please create this file with your FRED API key."
        )

    with open(SECRETS_FILE, "r") as f:
        secrets = yaml.safe_load(f)

    try:
        api_key = secrets["fred"]["api_key"]
    except KeyError:
        raise KeyError("FRED API key not found in secrets.yaml")

    return api_key


def collect_data() -> bool:
    """
    Main data collection workflow with parallel processing.

    This function:
    1. Loads API credentials
    2. Fetches 5 years of economic data from FRED (in parallel)
    3. Saves raw data to CSV files

    Extension 3: Parallel Processing
    - Uses ThreadPoolExecutor to fetch multiple series concurrently
    - Improves performance when fetching from remote APIs
    - Maintains data integrity through individual error handling

    Returns:
        True if successful, False otherwise
    """
    print("\n=== Economic Data Analysis Pipeline ===\n")
    print("[1/7] Fetching FRED data (parallel processing)...")

    try:
        # Load API key
        api_key = load_api_key()
        collector = FREDDataCollector(api_key)

        # Calculate date range (last 5 years)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)

        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # Parallel fetch using ThreadPoolExecutor
        results = {}
        errors = []

        def fetch_series_task(key: str, config: Dict) -> Tuple[str, int]:
            """Task function for parallel execution."""
            output_path = DATA_RAW_DIR / config["filename"]
            count = collector.fetch_and_save(
                config,
                start_str,
                end_str,
                output_path
            )
            return key, count

        # Execute fetches in parallel
        with ThreadPoolExecutor(max_workers=len(SERIES_CONFIG)) as executor:
            futures = {
                executor.submit(fetch_series_task, key, config): key
                for key, config in SERIES_CONFIG.items()
            }

            for future in as_completed(futures):
                key = futures[future]
                try:
                    _, count = future.result()
                    config = SERIES_CONFIG[key]
                    results[key] = count
                    print(f"  ✓ {config['series_id']} ({config['name']}): {count} observations")
                except Exception as e:
                    errors.append((key, str(e)))
                    print(f"  ✗ {key} failed: {e}", file=sys.stderr)

        if errors:
            print(f"\n  ✗ {len(errors)} series failed to fetch", file=sys.stderr)
            return False

        return True

    except Exception as e:
        print(f"  ✗ Data collection failed: {e}", file=sys.stderr)
        return False


def run_opinion_scraper() -> bool:
    """
    Run the public opinion scraper sub-agent.

    This sub-agent fetches public opinion data about the economy from YouGov
    and aggregates it to quarterly frequency to match economic indicators.

    Returns:
        True if successful, False otherwise
    """
    print("\n[2/7] Running opinion scraper sub-agent...")

    scraper_path = BASE_DIR / "agents" / "opinion_scraper.py"

    if not scraper_path.exists():
        print(f"  ✗ Opinion scraper not found at {scraper_path}", file=sys.stderr)
        print(f"  → Skipping opinion analysis")
        return True  # Non-fatal - continue without opinion data

    try:
        # Run opinion scraper sub-agent
        result = subprocess.run(
            [sys.executable, str(scraper_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # Check for output file
        opinion_path = DATA_RAW_DIR / "public_opinion.csv"
        if opinion_path.exists():
            print(f"  ✓ Opinion data collected: {opinion_path}")
            return True
        else:
            print("  ⚠ Opinion data file not created")
            print("  → Continuing without opinion analysis")
            return True  # Non-fatal

    except subprocess.CalledProcessError as e:
        print(f"  ⚠ Opinion scraper execution failed: {e}")
        print(f"  → Continuing without opinion analysis")
        return True  # Non-fatal - opinion data is optional
    except Exception as e:
        print(f"  ⚠ Opinion scraper error: {e}")
        print(f"  → Continuing without opinion analysis")
        return True  # Non-fatal


def run_validator() -> Tuple[bool, Optional[Dict]]:
    """
    Run the validation sub-agent.

    This sub-agent checks:
    - Data completeness
    - Date format and sequence
    - Value ranges
    - Series alignment

    Returns:
        Tuple of (success: bool, report: dict or None)
    """
    print("\n[3/7] Running validation sub-agent...")

    validator_path = BASE_DIR / "agents" / "validator.py"

    if not validator_path.exists():
        print(f"  ✗ Validator not found at {validator_path}", file=sys.stderr)
        return False, None

    try:
        # Run validator sub-agent
        result = subprocess.run(
            [sys.executable, str(validator_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # Load validation report
        report_path = OUTPUTS_DIR / "validation_report.json"
        with open(report_path, "r") as f:
            report = json.load(f)

        if report["status"] == "PASS":
            print("  ✓ Data validation passed")
            return True, report
        else:
            print("  ✗ Data validation failed:", file=sys.stderr)
            for check_name, check_result in report["checks"].items():
                if not check_result["passed"]:
                    print(f"    - {check_name}: {check_result['issues']}",
                          file=sys.stderr)
            return False, report

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Validator execution failed: {e}", file=sys.stderr)
        print(f"    STDERR: {e.stderr}", file=sys.stderr)
        return False, None
    except Exception as e:
        print(f"  ✗ Validator error: {e}", file=sys.stderr)
        return False, None


def run_plotter() -> bool:
    """
    Run the R visualization sub-agent.

    This sub-agent creates:
    - Multi-panel ggplot2 visualization
    - Professional styling with recession shading
    - High-resolution PNG output

    Returns:
        True if successful, False otherwise
    """
    print("\n[4/7] Running visualization sub-agent...")

    plotter_path = BASE_DIR / "agents" / "plotter.R"

    if not plotter_path.exists():
        print(f"  ✗ Plotter not found at {plotter_path}", file=sys.stderr)
        return False

    try:
        # Check if Rscript is available
        rscript_check = subprocess.run(
            ["which", "Rscript"],
            capture_output=True,
            text=True
        )

        if rscript_check.returncode != 0:
            print("  ✗ Rscript not found. Please install R.", file=sys.stderr)
            return False

        # Run R plotting sub-agent
        result = subprocess.run(
            ["Rscript", str(plotter_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(BASE_DIR)
        )

        output_path = OUTPUTS_DIR / "economic_dashboard.png"
        if output_path.exists():
            print(f"  ✓ Dashboard created: {output_path}")
            return True
        else:
            print("  ✗ Dashboard file not created", file=sys.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Plotter execution failed: {e}", file=sys.stderr)
        print(f"    STDERR: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  ✗ Plotter error: {e}", file=sys.stderr)
        return False


def run_analyzer() -> bool:
    """
    Run the statistical analysis sub-agent.

    Extension 1: Statistical Analyzer
    This sub-agent performs:
    - Correlation analysis between series
    - Granger causality tests
    - Descriptive statistics
    - LaTeX table generation

    Returns:
        True if successful, False otherwise
    """
    print("\n[5/7] Running statistical analysis sub-agent...")

    analyzer_path = BASE_DIR / "agents" / "analyzer.py"

    if not analyzer_path.exists():
        print(f"  ✗ Analyzer not found at {analyzer_path}", file=sys.stderr)
        return False

    try:
        # Run analyzer sub-agent
        result = subprocess.run(
            [sys.executable, str(analyzer_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # Check for output files
        stats_path = OUTPUTS_DIR / "statistical_analysis.json"
        if stats_path.exists():
            print("  ✓ Statistical analysis completed")
            print(f"    - JSON results: {stats_path}")
            print(f"    - LaTeX tables: correlation_matrix.tex, granger_causality.tex, descriptive_stats.tex")
            return True
        else:
            print("  ✗ Statistical analysis output not created", file=sys.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Analyzer execution failed: {e}", file=sys.stderr)
        print(f"    STDERR: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  ✗ Analyzer error: {e}", file=sys.stderr)
        return False


def run_reporter() -> bool:
    """
    Run the report generation sub-agent.

    Extension 2: Report Generator
    This sub-agent creates:
    - Comprehensive PDF report
    - Narrative interpretation of results
    - Combined visualizations and statistics
    - Professional formatting

    Returns:
        True if successful, False otherwise
    """
    print("\n[6/7] Running report generation sub-agent...")

    reporter_path = BASE_DIR / "agents" / "reporter.py"

    if not reporter_path.exists():
        print(f"  ✗ Reporter not found at {reporter_path}", file=sys.stderr)
        return False

    try:
        # Run reporter sub-agent
        result = subprocess.run(
            [sys.executable, str(reporter_path)],
            capture_output=True,
            text=True,
            check=True
        )

        # Check for output file
        report_path = OUTPUTS_DIR / "economic_report.pdf"
        if report_path.exists():
            print(f"  ✓ PDF report generated: {report_path}")
            return True
        else:
            print("  ✗ PDF report not created", file=sys.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Reporter execution failed: {e}", file=sys.stderr)
        print(f"    STDERR: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  ✗ Reporter error: {e}", file=sys.stderr)
        return False


def main():
    """
    Main orchestration workflow.

    This function coordinates the entire extended pipeline:
    1. Data collection (main agent) - with parallel fetching
    2. Opinion scraper (sub-agent 1) - public sentiment from YouGov
    3. Data validation (sub-agent 2) - quality checks
    4. Visualization (sub-agent 3) - R plotting
    5. Statistical analysis (sub-agent 4) - correlations, Granger tests, opinion analysis
    6. Report generation (sub-agent 5) - PDF with narrative

    The pipeline uses defensive programming:
    - Validation gates prevent bad data from propagating
    - Each stage checks for errors before proceeding
    - Clear status messages guide the user
    - Opinion data is optional (non-fatal if missing)
    """
    # Step 1: Collect data (with parallel processing)
    if not collect_data():
        print("\n❌ Pipeline failed at data collection stage.")
        sys.exit(1)

    # Step 2: Collect opinion data (optional - non-fatal)
    run_opinion_scraper()

    # Step 3: Validate data
    validation_passed, report = run_validator()
    if not validation_passed:
        print("\n❌ Pipeline failed at validation stage.")
        print("   Review validation_report.json for details.")
        sys.exit(1)

    # Step 4: Create visualizations
    if not run_plotter():
        print("\n❌ Pipeline failed at visualization stage.")
        sys.exit(1)

    # Step 5: Run statistical analysis
    if not run_analyzer():
        print("\n❌ Pipeline failed at statistical analysis stage.")
        sys.exit(1)

    # Step 6: Generate comprehensive report
    if not run_reporter():
        print("\n❌ Pipeline failed at report generation stage.")
        sys.exit(1)

    # Final summary
    print("\n[7/7] Pipeline Summary")
    print("\n" + "="*60)
    print("✅ Complete Pipeline Executed Successfully!")
    print("="*60)

    print("\n📊 Generated Outputs:")
    print(f"  1. Validation Report:    {OUTPUTS_DIR / 'validation_report.json'}")
    print(f"  2. Economic Dashboard:   {OUTPUTS_DIR / 'economic_dashboard.png'}")
    print(f"  3. Statistical Analysis: {OUTPUTS_DIR / 'statistical_analysis.json'}")
    print(f"  4. LaTeX Tables:         correlation_matrix.tex, granger_causality.tex,")
    print(f"                           descriptive_stats.tex, opinion_economy.tex (if available)")
    print(f"  5. Quarto Report:        {OUTPUTS_DIR / 'economic_report.qmd'}")
    print(f"  6. PDF Report:           {OUTPUTS_DIR / 'economic_report.pdf'}")

    print("\n📁 Data Files:")
    for config in SERIES_CONFIG.values():
        raw_path = DATA_RAW_DIR / config["filename"]
        val_path = DATA_VALIDATED_DIR / config["filename"]
        print(f"  - {config['name']}: {raw_path} → {val_path}")

    # Check if opinion data was collected
    opinion_path = DATA_RAW_DIR / "public_opinion.csv"
    if opinion_path.exists():
        print(f"  - Public Opinion: {opinion_path}")

    print("\n🎯 Key Features Demonstrated:")
    print("  ✓ Parallel data fetching (Extension 3)")
    print("  ✓ Statistical analysis with Granger causality (Extension 1)")
    print("  ✓ Opinion-economy correlation analysis with lagged indicators")
    print("  ✓ Automated PDF report generation (Extension 2)")
    print("  ✓ Multi-language integration (Python + R)")
    print("  ✓ Web scraping with fallback to sample data")
    print("  ✓ Sub-agent architecture with 6 specialized agents")
    print()


if __name__ == "__main__":
    main()
