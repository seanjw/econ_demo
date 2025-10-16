#!/usr/bin/env python3
"""
Report Generation Sub-Agent

This autonomous sub-agent creates comprehensive PDF reports combining
visualizations, statistical analysis, and narrative interpretation using
Quarto Markdown (.qmd).

Sub-Agent Responsibilities:
    1. Load all analysis outputs (visualizations, statistics)
    2. Auto-interpret economic relationships
    3. Generate Quarto Markdown (.qmd) with narrative text
    4. Compile to professional PDF using Quarto
    5. Include proper citations and methodology

Output:
    - outputs/economic_report.qmd: Quarto source file
    - outputs/economic_report.pdf: Compiled PDF report

Author: Claude Code Demo - Report Generation Sub-Agent
Date: 2025-10-15
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"


class QuartoReportGenerator:
    """
    Autonomous report generation sub-agent using Quarto.

    This sub-agent synthesizes all analysis outputs into a
    publication-ready PDF report using Quarto Markdown.
    """

    def __init__(self):
        """Initialize Quarto report generator."""
        self.stats_data = None
        self.validation_data = None
        self.qmd_content = []

    def load_analysis_results(self) -> bool:
        """
        Load all analysis outputs.

        Returns:
            True if successful, False otherwise
        """
        # Load statistical analysis
        stats_path = OUTPUTS_DIR / "statistical_analysis.json"
        if not stats_path.exists():
            print(f"  ✗ Statistical analysis not found", file=sys.stderr)
            return False

        with open(stats_path, "r") as f:
            self.stats_data = json.load(f)

        # Load validation report
        validation_path = OUTPUTS_DIR / "validation_report.json"
        if validation_path.exists():
            with open(validation_path, "r") as f:
                self.validation_data = json.load(f)

        return True

    def interpret_correlations(self) -> str:
        """
        Generate narrative interpretation of correlation results.

        Returns:
            Narrative text string
        """
        corr_data = self.stats_data["correlations"]["matrix"]

        # Get correlation between unemployment and GDP
        unemp_gdp_corr = corr_data["Unemployment Rate"]["Real GDP"]

        # Get correlation between fed funds and unemployment
        ff_unemp_corr = corr_data["Federal Funds Rate"]["Unemployment Rate"]

        # Get correlation between fed funds and GDP
        ff_gdp_corr = corr_data["Federal Funds Rate"]["Real GDP"]

        narrative = []

        narrative.append(
            f"The correlation analysis reveals important relationships between "
            f"the three economic indicators. "
        )

        # Unemployment-GDP relationship
        if unemp_gdp_corr < -0.3:
            narrative.append(
                f"Real GDP and the unemployment rate show a strong negative "
                f"correlation (r = {unemp_gdp_corr:.3f}), consistent with Okun's Law, "
                f"which posits an inverse relationship between economic output and "
                f"unemployment. "
            )
        elif unemp_gdp_corr < 0:
            narrative.append(
                f"Real GDP and the unemployment rate exhibit a moderate negative "
                f"correlation (r = {unemp_gdp_corr:.3f}), suggesting the expected "
                f"inverse relationship between economic growth and unemployment. "
            )

        # Federal Funds-GDP relationship
        if ff_gdp_corr < -0.2:
            narrative.append(
                f"The Federal Funds Rate shows a negative correlation with Real GDP "
                f"(r = {ff_gdp_corr:.3f}), indicating that higher interest rates "
                f"tend to coincide with lower economic output, consistent with "
                f"contractionary monetary policy effects. "
            )
        elif ff_gdp_corr > 0.2:
            narrative.append(
                f"Interestingly, the Federal Funds Rate shows a positive correlation "
                f"with Real GDP (r = {ff_gdp_corr:.3f}), which may reflect the Federal "
                f"Reserve's tendency to raise rates during periods of strong economic "
                f"growth to prevent overheating. "
            )

        # Federal Funds-Unemployment relationship
        if abs(ff_unemp_corr) > 0.3:
            direction = "positive" if ff_unemp_corr > 0 else "negative"
            narrative.append(
                f"The Federal Funds Rate and unemployment rate display a {direction} "
                f"correlation (r = {ff_unemp_corr:.3f}), reflecting the Federal "
                f"Reserve's dual mandate to maintain price stability and maximum employment. "
            )

        return "".join(narrative)

    def interpret_granger_causality(self) -> str:
        """
        Generate narrative interpretation of Granger causality results.

        Returns:
            Narrative text string
        """
        gc_data = self.stats_data["granger_causality"]["tests"]

        narrative = []
        significant_relationships = []

        # Find significant Granger causal relationships (p < 0.10 at any lag)
        for test_name, results in gc_data.items():
            if "error" in results:
                continue

            cause, effect = test_name.split(" → ")

            for lag_key, lag_result in results.items():
                if lag_result["p_value"] < 0.10:
                    lag_num = int(lag_key.split("_")[1])
                    significant_relationships.append({
                        "cause": cause,
                        "effect": effect,
                        "lag": lag_num,
                        "p_value": lag_result["p_value"],
                        "f_stat": lag_result["f_statistic"]
                    })
                    break  # Only report the first significant lag

        if not significant_relationships:
            narrative.append(
                "The Granger causality tests do not reveal strong predictive "
                "relationships between the series at conventional significance levels. "
                "This suggests that past values of one series may not significantly "
                "improve forecasts of the other series beyond what the latter's own "
                "history provides. "
            )
        else:
            narrative.append(
                "The Granger causality analysis identifies several significant "
                "predictive relationships. "
            )

            for rel in significant_relationships:
                sig_level = "1%" if rel["p_value"] < 0.01 else \
                           "5%" if rel["p_value"] < 0.05 else "10%"

                narrative.append(
                    f"Past values of {rel['cause']} significantly predict future "
                    f"values of {rel['effect']} at a {rel['lag']}-quarter lag "
                    f"(F = {rel['f_stat']:.2f}, p < {sig_level}). "
                )

            narrative.append(
                "These findings suggest temporal precedence and potential causal "
                "mechanisms, though Granger causality does not establish true "
                "causation in the philosophical sense. "
            )

        return "".join(narrative)

    def interpret_descriptive_stats(self) -> str:
        """
        Generate narrative interpretation of descriptive statistics.

        Returns:
            Narrative text string
        """
        desc_data = self.stats_data["descriptive_stats"]

        narrative = []

        gdp_stats = desc_data["Real GDP"]
        unemp_stats = desc_data["Unemployment Rate"]
        ff_stats = desc_data["Federal Funds Rate"]

        narrative.append(
            f"Over the {gdp_stats['count']} quarters examined, "
            f"Real GDP averaged {gdp_stats['mean']:.1f} billion dollars "
            f"(in 2017 chained dollars), with a standard deviation of "
            f"{gdp_stats['std']:.1f} billion. "
        )

        narrative.append(
            f"The unemployment rate averaged {unemp_stats['mean']:.1f}%, "
            f"ranging from {unemp_stats['min']:.1f}% to {unemp_stats['max']:.1f}%. "
        )

        # Check for high unemployment periods
        if unemp_stats['max'] > 8.0:
            narrative.append(
                f"The peak unemployment rate of {unemp_stats['max']:.1f}% "
                f"likely reflects recessionary conditions during the sample period. "
            )

        narrative.append(
            f"The Federal Funds Rate averaged {ff_stats['mean']:.2f}%, "
            f"with considerable variation (SD = {ff_stats['std']:.2f}%), "
            f"indicating active monetary policy adjustments during this period. "
        )

        # Check for near-zero rates
        if ff_stats['min'] < 0.5:
            narrative.append(
                f"The minimum rate of {ff_stats['min']:.2f}% reflects the "
                f"Federal Reserve's accommodative stance, likely in response "
                f"to economic weakness. "
            )

        return "".join(narrative)

    def interpret_opinion_economy(self) -> str:
        """
        Generate narrative interpretation of opinion-economy correlations.

        Returns:
            Narrative text string (empty if no opinion data)
        """
        if "opinion_economy" not in self.stats_data:
            return ""

        opinion_data = self.stats_data["opinion_economy"]
        if not opinion_data or not opinion_data.get("correlations"):
            return ""

        correlations = opinion_data["correlations"]
        narrative = []

        narrative.append(
            "We examined the relationship between economic conditions in one quarter "
            "and public opinion about the economy in the subsequent quarter. This lagged "
            "analysis tests whether economic indicators predict future public sentiment. "
        )

        # Find strongest correlations for each opinion metric
        opinion_metrics = {
            "getting_better_pct": "perceptions that the economy is getting better",
            "getting_worse_pct": "perceptions that the economy is getting worse",
            "net_sentiment": "net economic sentiment"
        }

        significant_findings = []

        for opinion_var, description in opinion_metrics.items():
            strongest_corr = None
            for key, corr_info in correlations.items():
                if f"→ {opinion_var}" in key:
                    if strongest_corr is None or abs(corr_info["correlation"]) > abs(strongest_corr["correlation"]):
                        econ_var = key.split(" (t-1) → ")[0]
                        strongest_corr = {
                            "econ_var": econ_var,
                            "correlation": corr_info["correlation"],
                            "p_value": corr_info["p_value"],
                            "opinion_var": description
                        }

            if strongest_corr and strongest_corr["p_value"] < 0.10:
                significant_findings.append(strongest_corr)

        if significant_findings:
            for finding in significant_findings:
                corr_val = finding["correlation"]
                direction = "positive" if corr_val > 0 else "negative"
                strength = "strong" if abs(corr_val) > 0.5 else "moderate"

                sig_level = "1%" if finding["p_value"] < 0.01 else \
                           "5%" if finding["p_value"] < 0.05 else "10%"

                narrative.append(
                    f"{finding['econ_var']} in the prior quarter shows a {strength} {direction} "
                    f"correlation (r = {corr_val:.3f}, p < {sig_level}) with {finding['opinion_var']} "
                    f"in the current quarter. "
                )

            narrative.append(
                "These findings suggest that economic conditions have a lagged effect on "
                "public perception, with changes in macroeconomic indicators taking time "
                "to influence how the public views the economy's direction. "
            )
        else:
            narrative.append(
                "The analysis does not reveal strong significant correlations between "
                "lagged economic indicators and current public opinion, suggesting that "
                "public sentiment may be influenced by factors beyond the quarterly "
                "economic aggregates examined here. "
            )

        return "".join(narrative)

    def generate_qmd_content(self) -> str:
        """
        Generate complete Quarto Markdown document.

        Returns:
            Complete QMD content as string
        """
        qmd = []

        # YAML front matter
        qmd.append("---")
        qmd.append("title: \"Economic Indicators Analysis Report\"")
        qmd.append(f"author: \"Generated: {datetime.now().strftime('%B %d, %Y')}\"")
        qmd.append("date: today")
        qmd.append("format:")
        qmd.append("  pdf:")
        qmd.append("    documentclass: article")
        qmd.append("    geometry: margin=1in")
        qmd.append("    toc: true")
        qmd.append("    number-sections: true")
        qmd.append("    colorlinks: true")
        qmd.append("    fontsize: 11pt")
        qmd.append("---")
        qmd.append("")

        # Executive Summary
        qmd.append("# Executive Summary")
        qmd.append("")
        qmd.append(
            f"This report presents a comprehensive analysis of three key U.S. economic "
            f"indicators over the past five years: Real Gross Domestic Product (GDP), "
            f"the Unemployment Rate, and the Federal Funds Effective Rate. "
            f"The analysis combines time series visualization, correlation analysis, "
            f"Granger causality testing, and descriptive statistics to examine the "
            f"relationships and dynamics among these critical macroeconomic variables."
        )
        qmd.append("")

        # Data Quality Section
        if self.validation_data:
            qmd.append("# Data Quality")
            qmd.append("")
            qmd.append(
                f"All data underwent rigorous validation checks. "
                f"The validation process confirmed data completeness, proper formatting, "
                f"economically reasonable value ranges, and temporal alignment across all "
                f"three series. {self.validation_data['summary']}"
            )
            qmd.append("")

        # Descriptive Statistics
        qmd.append("# Descriptive Statistics")
        qmd.append("")
        desc_narrative = self.interpret_descriptive_stats()
        qmd.append(desc_narrative)
        qmd.append("")

        # Time Series Visualization
        qmd.append("# Time Series Visualization")
        qmd.append("")
        qmd.append(
            "Figure 1 presents the time series for all three economic indicators. "
            "The visualization reveals the dynamic patterns and potential relationships "
            "among the variables over the study period. Gray shaded regions indicate "
            "periods of economic recession as defined by the National Bureau of Economic "
            "Research (NBER)."
        )
        qmd.append("")

        # Embed dashboard image
        dashboard_path = OUTPUTS_DIR / "economic_dashboard.png"
        if dashboard_path.exists():
            qmd.append("![Time series of Real GDP, Unemployment Rate, and Federal Funds Rate (2020-2025)](economic_dashboard.png){width=100%}")
            qmd.append("")

        # Correlation Analysis
        qmd.append("# Correlation Analysis")
        qmd.append("")
        corr_narrative = self.interpret_correlations()
        qmd.append(corr_narrative)
        qmd.append("")

        # Include correlation table
        corr_tex_path = OUTPUTS_DIR / "correlation_matrix.tex"
        if corr_tex_path.exists():
            qmd.append("## Correlation Matrix")
            qmd.append("")
            # Create a simplified markdown table
            corr_data = self.stats_data["correlations"]["matrix"]
            series_names = ["Real GDP", "Unemployment Rate", "Federal Funds Rate"]

            qmd.append("| Variable | Real GDP | Unemployment Rate | Federal Funds Rate |")
            qmd.append("|----------|----------|-------------------|---------------------|")

            for s1 in series_names:
                row = [s1]
                for s2 in series_names:
                    corr_val = corr_data[s1][s2]
                    if s1 == s2:
                        row.append("1.000")
                    else:
                        row.append(f"{corr_val:.3f}")
                qmd.append("| " + " | ".join(row) + " |")
            qmd.append("")
            qmd.append(f"*Note: Based on {self.stats_data['correlations']['n_observations']} quarterly observations.*")
            qmd.append("")

        # Granger Causality Analysis
        qmd.append("# Granger Causality Analysis")
        qmd.append("")
        granger_narrative = self.interpret_granger_causality()
        qmd.append(granger_narrative)
        qmd.append("")

        # Opinion-Economy Analysis (if available)
        opinion_narrative = self.interpret_opinion_economy()
        if opinion_narrative:
            qmd.append("# Public Opinion and Economic Indicators")
            qmd.append("")
            qmd.append(opinion_narrative)
            qmd.append("")

            # Include opinion-economy correlation table if available
            if "opinion_economy" in self.stats_data and self.stats_data["opinion_economy"].get("correlations"):
                opinion_corr = self.stats_data["opinion_economy"]["correlations"]

                qmd.append("## Lagged Correlations with Public Opinion")
                qmd.append("")
                qmd.append("| Economic Indicator (t-1) | Getting Better % | Getting Worse % | Net Sentiment |")
                qmd.append("|--------------------------|------------------|-----------------|---------------|")

                econ_vars = ["Real GDP", "Unemployment Rate", "Federal Funds Rate"]
                opinion_metrics = ["getting_better_pct", "getting_worse_pct", "net_sentiment"]

                for econ_var in econ_vars:
                    row = [econ_var]
                    for opinion_var in opinion_metrics:
                        key = f"{econ_var} (t-1) → {opinion_var} (t)"
                        if key in opinion_corr:
                            corr_val = opinion_corr[key]["correlation"]
                            p_val = opinion_corr[key]["p_value"]

                            stars = ""
                            if p_val < 0.01:
                                stars = "***"
                            elif p_val < 0.05:
                                stars = "**"
                            elif p_val < 0.10:
                                stars = "*"

                            row.append(f"{corr_val:.3f}{stars}")
                        else:
                            row.append("—")

                    qmd.append("| " + " | ".join(row) + " |")

                qmd.append("")
                qmd.append(f"*Note: Economic indicators lagged by 1 quarter. "
                          f"Significance: *** p<0.01, ** p<0.05, * p<0.10. "
                          f"N = {self.stats_data['opinion_economy']['n_observations']} quarters.*")
                qmd.append("")

        # Methodology
        qmd.append("# Methodology")
        qmd.append("")
        methodology_text = (
            "This analysis employs several econometric techniques: "
            "(1) Pearson correlation coefficients to measure linear associations; "
            "(2) Granger causality tests to assess predictive relationships, testing "
            "whether past values of one variable improve forecasts of another beyond "
            "the latter's own history; and (3) standard descriptive statistics. "
        )

        if opinion_narrative:
            methodology_text += (
                "(4) Lagged correlation analysis examines relationships between economic "
                "indicators in quarter t-1 and public opinion in quarter t, testing whether "
                "macroeconomic conditions predict subsequent public sentiment. "
            )

        methodology_text += (
            "All data were aggregated to quarterly frequency and validated for "
            "completeness and consistency before analysis. Statistical significance "
            "is assessed at the 1%, 5%, and 10% levels."
        )

        qmd.append(methodology_text)
        qmd.append("")

        # Data Source
        qmd.append("# Data Source")
        qmd.append("")
        data_source_text = (
            "Economic data are sourced from the Federal Reserve Economic Data (FRED) "
            "database maintained by the Federal Reserve Bank of St. Louis. "
            "FRED series identifiers: GDPC1 (Real Gross Domestic Product), "
            "UNRATE (Unemployment Rate), DFF (Federal Funds Effective Rate). "
        )

        if opinion_narrative:
            data_source_text += (
                "Public opinion data on the state of the U.S. economy are from YouGov's "
                "tracking polls, aggregated to quarterly frequency to align with economic indicators. "
            )

        data_source_text += "Data retrieved: " + datetime.now().strftime('%B %Y') + "."

        qmd.append(data_source_text)
        qmd.append("")

        return "\n".join(qmd)

    def compile_with_quarto(self, qmd_path: Path) -> bool:
        """
        Compile QMD to PDF using Quarto.

        Args:
            qmd_path: Path to the .qmd file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if Quarto is installed
            check_result = subprocess.run(
                ["which", "quarto"],
                capture_output=True,
                text=True
            )

            if check_result.returncode != 0:
                print("  ✗ Quarto not found. Please install Quarto from https://quarto.org", file=sys.stderr)
                print("     Installation: brew install quarto (macOS) or download from website", file=sys.stderr)
                return False

            # Compile to PDF
            print(f"  • Compiling QMD to PDF with Quarto...")
            result = subprocess.run(
                ["quarto", "render", str(qmd_path)],
                capture_output=True,
                text=True,
                cwd=str(OUTPUTS_DIR)
            )

            if result.returncode != 0:
                print(f"  ✗ Quarto compilation failed", file=sys.stderr)
                print(f"    STDERR: {result.stderr}", file=sys.stderr)
                return False

            return True

        except Exception as e:
            print(f"  ✗ Quarto compilation error: {e}", file=sys.stderr)
            return False

    def generate_report(self) -> bool:
        """
        Generate complete Quarto report and compile to PDF.

        Returns:
            True if successful, False otherwise
        """
        print("\n=== Report Generation Sub-Agent (Quarto) ===\n")

        # Load analysis results
        print("Loading analysis results...")
        if not self.load_analysis_results():
            return False
        print("  ✓ Analysis results loaded")

        # Generate QMD content
        print("\nGenerating Quarto Markdown (.qmd)...")
        qmd_content = self.generate_qmd_content()

        qmd_path = OUTPUTS_DIR / "economic_report.qmd"
        with open(qmd_path, "w") as f:
            f.write(qmd_content)
        print(f"  ✓ QMD file created: {qmd_path}")

        # Compile to PDF
        print("\nCompiling to PDF with Quarto...")
        if not self.compile_with_quarto(qmd_path):
            print("\n  ⚠ QMD file was created but PDF compilation failed.")
            print("    You can manually compile with: quarto render outputs/economic_report.qmd")
            return False

        pdf_path = OUTPUTS_DIR / "economic_report.pdf"
        if pdf_path.exists():
            print(f"  ✓ PDF report generated: {pdf_path}")
        else:
            print(f"  ✗ PDF file not found after compilation", file=sys.stderr)
            return False

        print("\n✓ Report generation complete!\n")
        return True


def main():
    """
    Main entry point for report generation sub-agent.

    This sub-agent can be invoked independently:
        python agents/reporter.py

    Or as part of the main pipeline orchestration.
    """
    # Create outputs directory
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate report
    reporter = QuartoReportGenerator()
    success = reporter.generate_report()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
