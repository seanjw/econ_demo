#!/usr/bin/env python3
"""
Statistical Analysis Sub-Agent

This autonomous sub-agent specializes in econometric analysis of time series data.
It performs advanced statistical tests and generates professional LaTeX tables.

Sub-Agent Responsibilities:
    1. Correlation Analysis: Compute pairwise correlations between series
    2. Granger Causality Tests: Test predictive relationships
    3. Descriptive Statistics: Summary statistics for each series
    4. Opinion-Economy Analysis: Test relationships between lagged economic
       indicators and public opinion (if opinion data available)
    5. LaTeX Table Generation: Professional academic tables

Output:
    - outputs/statistical_analysis.json: Detailed statistical results
    - outputs/correlation_matrix.tex: LaTeX correlation table
    - outputs/granger_causality.tex: LaTeX causality test results
    - outputs/descriptive_stats.tex: LaTeX descriptive statistics
    - outputs/opinion_economy.tex: LaTeX opinion-economy table (if available)

Author: Claude Code Demo - Statistical Analysis Sub-Agent
Date: 2025-10-15
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tools.sm_exceptions import InterpolationWarning

warnings.filterwarnings('ignore', category=InterpolationWarning)

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_VALIDATED_DIR = BASE_DIR / "data" / "validated"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Series metadata for reporting
SERIES_INFO = {
    "gdp.csv": {
        "name": "Real GDP",
        "latex_name": "Real GDP",
        "units": "Billions of 2017\\$"
    },
    "unemployment.csv": {
        "name": "Unemployment Rate",
        "latex_name": "Unemployment Rate",
        "units": "Percent"
    },
    "fed_funds.csv": {
        "name": "Federal Funds Rate",
        "latex_name": "Fed Funds Rate",
        "units": "Percent"
    }
}

# Reverse mapping: series name -> filename for LaTeX generation
NAME_TO_FILE = {
    info["name"]: filename
    for filename, info in SERIES_INFO.items()
}


class StatisticalAnalyzer:
    """
    Autonomous statistical analysis sub-agent.

    This sub-agent performs econometric analysis independently and
    generates publication-ready LaTeX tables.
    """

    def __init__(self):
        """Initialize statistical analyzer."""
        self.data = {}
        self.opinion_data = None
        self.results = {
            "correlations": {},
            "granger_causality": {},
            "descriptive_stats": {},
            "opinion_economy": {}
        }

    def load_data(self) -> bool:
        """
        Load validated data files.

        Returns:
            True if successful, False otherwise
        """
        for filename in SERIES_INFO.keys():
            file_path = DATA_VALIDATED_DIR / filename

            if not file_path.exists():
                print(f"  ✗ Data file not found: {filename}", file=sys.stderr)
                return False

            try:
                df = pd.read_csv(file_path)
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date")

                series_name = SERIES_INFO[filename]["name"]
                self.data[series_name] = df

            except Exception as e:
                print(f"  ✗ Failed to load {filename}: {e}", file=sys.stderr)
                return False

        return True

    def load_opinion_data(self) -> bool:
        """
        Load public opinion data from raw directory.

        Returns:
            True if successful, False otherwise
        """
        opinion_path = DATA_RAW_DIR / "public_opinion.csv"

        if not opinion_path.exists():
            print(f"  ⚠ Opinion data not found: {opinion_path}")
            print(f"  → Skipping opinion analysis")
            return False

        try:
            df = pd.read_csv(opinion_path)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            self.opinion_data = df
            return True

        except Exception as e:
            print(f"  ✗ Failed to load opinion data: {e}", file=sys.stderr)
            return False

    def compute_correlations(self) -> Dict:
        """
        Compute pairwise correlations between all series.

        Returns:
            Dictionary of correlation coefficients and p-values
        """
        # Merge all series using quarter periods to handle date format differences
        merged = None
        for series_name, df in self.data.items():
            df_copy = df.copy()
            df_copy = df_copy.rename(columns={"value": series_name})
            df_copy["quarter"] = df_copy["date"].dt.to_period("Q")

            if merged is None:
                merged = df_copy[["date", "quarter", series_name]]
            else:
                merged = merged.merge(
                    df_copy[["quarter", series_name]],
                    on="quarter",
                    how="inner"
                )

        # Compute correlation matrix
        series_names = list(self.data.keys())
        corr_matrix = merged[series_names].corr()

        # Compute p-values for each correlation
        n = len(merged)
        p_values = pd.DataFrame(
            np.zeros((len(series_names), len(series_names))),
            index=series_names,
            columns=series_names
        )

        for i, s1 in enumerate(series_names):
            for j, s2 in enumerate(series_names):
                if i < j:
                    r = corr_matrix.loc[s1, s2]
                    # t-statistic for correlation
                    if abs(r) < 1.0:  # Avoid division by zero for perfect correlation
                        t_stat = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)
                        p_val = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
                    else:
                        p_val = 0.0  # Perfect correlation is always significant
                    p_values.loc[s1, s2] = p_val
                    p_values.loc[s2, s1] = p_val

        self.results["correlations"] = {
            "matrix": corr_matrix.to_dict(),
            "p_values": p_values.to_dict(),
            "n_observations": n
        }

        return self.results["correlations"]

    def granger_causality_analysis(self, max_lag: int = 4) -> Dict:
        """
        Perform Granger causality tests between all pairs of series.

        Args:
            max_lag: Maximum number of lags to test

        Returns:
            Dictionary of Granger causality test results
        """
        # Merge all series using quarter periods to handle date format differences
        merged = None
        for series_name, df in self.data.items():
            df_copy = df.copy()
            df_copy = df_copy.rename(columns={"value": series_name})
            df_copy["quarter"] = df_copy["date"].dt.to_period("Q")

            if merged is None:
                merged = df_copy[["date", "quarter", series_name]]
            else:
                merged = merged.merge(
                    df_copy[["quarter", series_name]],
                    on="quarter",
                    how="inner"
                )

        series_names = list(self.data.keys())
        granger_results = {}

        # Test all pairs (X → Y)
        for cause in series_names:
            for effect in series_names:
                if cause != effect:
                    test_name = f"{cause} → {effect}"

                    try:
                        # Prepare data: [Y, X] format for statsmodels
                        test_data = merged[[effect, cause]].values

                        # Run Granger causality test
                        gc_res = grangercausalitytests(
                            test_data,
                            maxlag=max_lag,
                            verbose=False
                        )

                        # Extract F-statistics and p-values for each lag
                        lag_results = {}
                        for lag in range(1, max_lag + 1):
                            f_test = gc_res[lag][0]['ssr_ftest']
                            lag_results[f"lag_{lag}"] = {
                                "f_statistic": float(f_test[0]),
                                "p_value": float(f_test[1]),
                                "df1": int(f_test[2]),
                                "df2": int(f_test[3])
                            }

                        granger_results[test_name] = lag_results

                    except Exception as e:
                        granger_results[test_name] = {
                            "error": str(e)
                        }

        self.results["granger_causality"] = {
            "max_lag": max_lag,
            "tests": granger_results
        }

        return self.results["granger_causality"]

    def compute_descriptive_stats(self) -> Dict:
        """
        Compute descriptive statistics for each series.

        Returns:
            Dictionary of descriptive statistics
        """
        stats_dict = {}

        for series_name, df in self.data.items():
            values = df["value"]

            stats_dict[series_name] = {
                "count": int(len(values)),
                "mean": float(values.mean()),
                "std": float(values.std()),
                "min": float(values.min()),
                "q25": float(values.quantile(0.25)),
                "median": float(values.median()),
                "q75": float(values.quantile(0.75)),
                "max": float(values.max()),
                "skewness": float(values.skew()),
                "kurtosis": float(values.kurtosis())
            }

        self.results["descriptive_stats"] = stats_dict
        return stats_dict

    def analyze_opinion_correlations(self) -> Dict:
        """
        Analyze relationships between prior quarter economic data and current opinion.

        This tests whether economic conditions in quarter t-1 predict
        public sentiment in quarter t.

        Returns:
            Dictionary of correlation results between lagged economics and opinion
        """
        if self.opinion_data is None:
            return {}

        # Merge all economic series using quarter periods
        # (handles discrepancies between quarter-start vs quarter-end dates)
        merged_econ = None
        for series_name, df in self.data.items():
            df_copy = df.copy()
            df_copy = df_copy.rename(columns={"value": series_name})
            df_copy["quarter"] = df_copy["date"].dt.to_period("Q")

            if merged_econ is None:
                merged_econ = df_copy[["date", "quarter", series_name]]
            else:
                merged_econ = merged_econ.merge(
                    df_copy[["quarter", series_name]],
                    on="quarter",
                    how="inner"
                )

        # Create lagged economic indicators (lag by 1 quarter)
        # This shifts economic data forward in time, so we can match
        # quarter t-1 economics with quarter t opinion
        econ_lagged = merged_econ.copy()
        econ_lagged["quarter"] = econ_lagged["quarter"] + 1  # Shift forward by 1 quarter

        # Prepare opinion data with quarter periods
        opinion_with_quarter = self.opinion_data.copy()
        opinion_with_quarter["quarter"] = opinion_with_quarter["date"].dt.to_period("Q")

        # Merge lagged economics with current opinion based on quarter
        merged = opinion_with_quarter.merge(
            econ_lagged.drop(columns=["date"], errors='ignore'),
            on="quarter",
            how="inner"
        )
        merged = merged.drop(columns=["quarter"])

        if len(merged) == 0:
            print("  ⚠ No overlapping dates between opinion and economic data")
            return {}

        # Define opinion metrics to analyze
        opinion_metrics = [
            "getting_better_pct",
            "getting_worse_pct",
            "staying_same_pct",
            "net_sentiment"
        ]

        # Compute correlations between lagged economics and opinion
        economic_series = list(self.data.keys())
        correlations = {}

        for econ_var in economic_series:
            for opinion_var in opinion_metrics:
                if econ_var in merged.columns and opinion_var in merged.columns:
                    # Compute correlation
                    corr_result = stats.pearsonr(
                        merged[econ_var],
                        merged[opinion_var]
                    )

                    correlations[f"{econ_var} (t-1) → {opinion_var} (t)"] = {
                        "correlation": float(corr_result[0]),
                        "p_value": float(corr_result[1]),
                        "n_observations": len(merged)
                    }

        self.results["opinion_economy"] = {
            "correlations": correlations,
            "n_observations": len(merged),
            "lag_quarters": 1,
            "note": "Economic indicators lagged by 1 quarter to test predictive relationships"
        }

        return self.results["opinion_economy"]

    def generate_correlation_latex(self) -> str:
        """
        Generate LaTeX table for correlation matrix.

        Returns:
            LaTeX table string
        """
        corr_data = self.results["correlations"]
        series_names = list(self.data.keys())

        latex = []
        latex.append("% Correlation Matrix")
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Correlation Matrix of Economic Indicators}")
        latex.append("\\label{tab:correlations}")
        latex.append("\\begin{tabular}{l" + "c" * len(series_names) + "}")
        latex.append("\\hline\\hline")

        # Header row
        header = " & " + " & ".join([
            SERIES_INFO[NAME_TO_FILE[s]]["latex_name"]
            for s in series_names
        ]) + " \\\\"
        latex.append(header)
        latex.append("\\hline")

        # Data rows
        for i, s1 in enumerate(series_names):
            row = [SERIES_INFO[NAME_TO_FILE[s1]]["latex_name"]]

            for j, s2 in enumerate(series_names):
                corr_val = corr_data["matrix"][s1][s2]

                if i == j:
                    # Diagonal
                    cell = "1.000"
                elif i < j:
                    # Upper triangle: correlation with significance stars
                    p_val = corr_data["p_values"][s1][s2]

                    stars = ""
                    if p_val < 0.01:
                        stars = "***"
                    elif p_val < 0.05:
                        stars = "**"
                    elif p_val < 0.10:
                        stars = "*"

                    cell = f"{corr_val:.3f}{stars}"
                else:
                    # Lower triangle: blank (for cleaner table)
                    cell = ""

                row.append(cell)

            latex.append(" & ".join(row) + " \\\\")

        latex.append("\\hline\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\begin{flushleft}")
        latex.append("\\footnotesize")
        latex.append(f"\\textit{{Note:}} Based on {corr_data['n_observations']} quarterly observations. ")
        latex.append("Significance levels: *** p$<$0.01, ** p$<$0.05, * p$<$0.10.")
        latex.append("\\end{flushleft}")
        latex.append("\\end{table}")

        return "\n".join(latex)

    def generate_granger_latex(self) -> str:
        """
        Generate LaTeX table for Granger causality tests.

        Returns:
            LaTeX table string
        """
        gc_data = self.results["granger_causality"]
        max_lag = gc_data["max_lag"]

        latex = []
        latex.append("% Granger Causality Test Results")
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Granger Causality Test Results}")
        latex.append("\\label{tab:granger}")
        latex.append("\\begin{tabular}{ll" + "c" * max_lag + "}")
        latex.append("\\hline\\hline")

        # Header
        header = "Cause & Effect & " + " & ".join([
            f"Lag {i}" for i in range(1, max_lag + 1)
        ]) + " \\\\"
        latex.append(header)
        latex.append("\\hline")

        # Data rows
        for test_name, results in gc_data["tests"].items():
            if "error" in results:
                continue

            cause, effect = test_name.split(" → ")
            row = [
                SERIES_INFO[NAME_TO_FILE[cause]]["latex_name"],
                SERIES_INFO[NAME_TO_FILE[effect]]["latex_name"]
            ]

            for lag in range(1, max_lag + 1):
                lag_key = f"lag_{lag}"
                if lag_key in results:
                    f_stat = results[lag_key]["f_statistic"]
                    p_val = results[lag_key]["p_value"]

                    stars = ""
                    if p_val < 0.01:
                        stars = "***"
                    elif p_val < 0.05:
                        stars = "**"
                    elif p_val < 0.10:
                        stars = "*"

                    cell = f"{f_stat:.2f}{stars}"
                else:
                    cell = "---"

                row.append(cell)

            latex.append(" & ".join(row) + " \\\\")

        latex.append("\\hline\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\begin{flushleft}")
        latex.append("\\footnotesize")
        latex.append("\\textit{Note:} F-statistics from Granger causality tests. ")
        latex.append("Significance levels: *** p$<$0.01, ** p$<$0.05, * p$<$0.10. ")
        latex.append("H$_0$: Cause does not Granger-cause Effect.")
        latex.append("\\end{flushleft}")
        latex.append("\\end{table}")

        return "\n".join(latex)

    def generate_descriptive_latex(self) -> str:
        """
        Generate LaTeX table for descriptive statistics.

        Returns:
            LaTeX table string
        """
        stats_data = self.results["descriptive_stats"]

        latex = []
        latex.append("% Descriptive Statistics")
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Descriptive Statistics}")
        latex.append("\\label{tab:descriptive}")
        latex.append("\\begin{tabular}{lcccccc}")
        latex.append("\\hline\\hline")
        latex.append("Variable & N & Mean & Std Dev & Min & Median & Max \\\\")
        latex.append("\\hline")

        for series_name, stats in stats_data.items():
            latex_name = SERIES_INFO[NAME_TO_FILE[series_name]]["latex_name"]
            units = SERIES_INFO[NAME_TO_FILE[series_name]]["units"]

            row = [
                f"{latex_name}",
                f"{stats['count']}",
                f"{stats['mean']:.2f}",
                f"{stats['std']:.2f}",
                f"{stats['min']:.2f}",
                f"{stats['median']:.2f}",
                f"{stats['max']:.2f}"
            ]

            latex.append(" & ".join(row) + " \\\\")

        latex.append("\\hline\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\begin{flushleft}")
        latex.append("\\footnotesize")
        latex.append("\\textit{Note:} Descriptive statistics for quarterly economic indicators.")
        latex.append("\\end{flushleft}")
        latex.append("\\end{table}")

        return "\n".join(latex)

    def generate_opinion_latex(self) -> str:
        """
        Generate LaTeX table for opinion-economy correlations.

        Returns:
            LaTeX table string
        """
        if not self.results["opinion_economy"] or not self.results["opinion_economy"].get("correlations"):
            return "% No opinion data available\n"

        opinion_data = self.results["opinion_economy"]
        correlations = opinion_data["correlations"]

        # Organize results by economic variable
        economic_vars = list(self.data.keys())
        opinion_metrics = [
            ("getting_better_pct", "Getting Better \\%"),
            ("getting_worse_pct", "Getting Worse \\%"),
            ("staying_same_pct", "Staying Same \\%"),
            ("net_sentiment", "Net Sentiment")
        ]

        latex = []
        latex.append("% Opinion-Economy Correlations (Lagged)")
        latex.append("\\begin{table}[htbp]")
        latex.append("\\centering")
        latex.append("\\caption{Prior Quarter Economic Indicators and Public Opinion}")
        latex.append("\\label{tab:opinion_economy}")
        latex.append("\\begin{tabular}{l" + "c" * len(opinion_metrics) + "}")
        latex.append("\\hline\\hline")

        # Header row
        header = "Economic Indicator (t-1) & " + " & ".join([
            metric[1] for metric in opinion_metrics
        ]) + " \\\\"
        latex.append(header)
        latex.append("\\hline")

        # Data rows - one row per economic variable
        for econ_var in economic_vars:
            econ_latex_name = SERIES_INFO[NAME_TO_FILE[econ_var]]["latex_name"]
            row = [econ_latex_name]

            for opinion_var, _ in opinion_metrics:
                key = f"{econ_var} (t-1) → {opinion_var} (t)"

                if key in correlations:
                    corr = correlations[key]["correlation"]
                    p_val = correlations[key]["p_value"]

                    stars = ""
                    if p_val < 0.01:
                        stars = "***"
                    elif p_val < 0.05:
                        stars = "**"
                    elif p_val < 0.10:
                        stars = "*"

                    cell = f"{corr:.3f}{stars}"
                else:
                    cell = "---"

                row.append(cell)

            latex.append(" & ".join(row) + " \\\\")

        latex.append("\\hline\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\begin{flushleft}")
        latex.append("\\footnotesize")
        latex.append(f"\\textit{{Note:}} Based on {opinion_data['n_observations']} quarterly observations. ")
        latex.append("Economic indicators are lagged by 1 quarter (t-1) relative to opinion data (t). ")
        latex.append("Significance levels: *** p$<$0.01, ** p$<$0.05, * p$<$0.10.")
        latex.append("\\end{flushleft}")
        latex.append("\\end{table}")

        return "\n".join(latex)

    def run_analysis(self) -> bool:
        """
        Run complete statistical analysis pipeline.

        Returns:
            True if successful, False otherwise
        """
        print("\n=== Statistical Analysis Sub-Agent ===\n")

        # Load data
        print("Loading validated data...")
        if not self.load_data():
            return False

        print(f"  ✓ Loaded {len(self.data)} series")

        # Run analyses
        print("\nComputing correlations...")
        self.compute_correlations()
        print("  ✓ Correlation matrix computed")

        print("\nRunning Granger causality tests...")
        self.granger_causality_analysis(max_lag=4)
        print("  ✓ Granger causality tests completed")

        print("\nComputing descriptive statistics...")
        self.compute_descriptive_stats()
        print("  ✓ Descriptive statistics computed")

        # Opinion analysis (optional - may not be available)
        print("\nLoading public opinion data...")
        if self.load_opinion_data():
            print(f"  ✓ Loaded opinion data")
            print("\nAnalyzing opinion-economy relationships...")
            self.analyze_opinion_correlations()
            print("  ✓ Opinion correlations computed")
        else:
            print("  → Opinion analysis skipped")

        # Generate outputs
        print("\nGenerating outputs...")

        # Save JSON results
        json_path = OUTPUTS_DIR / "statistical_analysis.json"
        with open(json_path, "w") as f:
            json.dump(self.results, indent=2, fp=f)
        print(f"  ✓ JSON results: {json_path}")

        # Generate LaTeX tables
        corr_latex = self.generate_correlation_latex()
        corr_path = OUTPUTS_DIR / "correlation_matrix.tex"
        with open(corr_path, "w") as f:
            f.write(corr_latex)
        print(f"  ✓ LaTeX correlation table: {corr_path}")

        granger_latex = self.generate_granger_latex()
        granger_path = OUTPUTS_DIR / "granger_causality.tex"
        with open(granger_path, "w") as f:
            f.write(granger_latex)
        print(f"  ✓ LaTeX Granger table: {granger_path}")

        desc_latex = self.generate_descriptive_latex()
        desc_path = OUTPUTS_DIR / "descriptive_stats.tex"
        with open(desc_path, "w") as f:
            f.write(desc_latex)
        print(f"  ✓ LaTeX descriptive stats: {desc_path}")

        # Generate opinion table if available
        if self.opinion_data is not None:
            opinion_latex = self.generate_opinion_latex()
            opinion_path = OUTPUTS_DIR / "opinion_economy.tex"
            with open(opinion_path, "w") as f:
                f.write(opinion_latex)
            print(f"  ✓ LaTeX opinion-economy table: {opinion_path}")

        print("\n✓ Statistical analysis complete!\n")

        return True


def main():
    """
    Main entry point for statistical analysis sub-agent.

    This sub-agent can be invoked independently:
        python agents/analyzer.py

    Or as part of the main pipeline orchestration.
    """
    # Create outputs directory
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Run analysis
    analyzer = StatisticalAnalyzer()
    success = analyzer.run_analysis()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
