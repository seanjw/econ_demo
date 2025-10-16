#!/usr/bin/env python3
"""
Data Validation Sub-Agent

This autonomous sub-agent is responsible for ensuring data quality and integrity.
It performs comprehensive validation checks on economic time series data before
allowing it to proceed to visualization and analysis stages.

Sub-Agent Responsibilities:
    1. Completeness: Verify no missing dates in quarterly sequence
    2. Format: Ensure dates follow ISO format (YYYY-MM-DD)
    3. Sequence: Confirm chronological ordering
    4. Ranges: Check economically reasonable values
    5. Alignment: Verify all series cover matching time periods

Output:
    - validation_report.json: Detailed pass/fail results
    - Copies validated data to data/validated/ if all checks pass

Author: Claude Code Demo - Validation Sub-Agent
Date: 2025-10-15
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_VALIDATED_DIR = BASE_DIR / "data" / "validated"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Economic validity ranges (reasonable bounds for quarterly data)
VALUE_RANGES = {
    "gdp.csv": {
        "min": 10000.0,  # $10 trillion in billions (minimum reasonable recent GDP)
        "max": 30000.0,  # $30 trillion in billions (maximum reasonable near-term GDP)
        "name": "Real GDP (Billions of Chained 2017 Dollars)"
    },
    "unemployment.csv": {
        "min": 0.0,    # 0% unemployment (theoretical minimum)
        "max": 30.0,   # 30% unemployment (extreme crisis)
        "name": "Unemployment Rate"
    },
    "fed_funds.csv": {
        "min": 0.0,    # 0% fed funds (zero lower bound)
        "max": 25.0,   # 25% fed funds (extreme inflation fighting)
        "name": "Federal Funds Rate"
    }
}


class ValidationResult:
    """Container for validation check results."""

    def __init__(self, check_name: str):
        self.check_name = check_name
        self.passed = True
        self.issues = []

    def add_issue(self, issue: str):
        """Record a validation issue."""
        self.passed = False
        self.issues.append(issue)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "passed": self.passed,
            "issues": self.issues
        }


class DataValidator:
    """
    Autonomous validation sub-agent.

    This sub-agent operates independently to ensure data quality.
    It can be invoked standalone or as part of a larger pipeline.
    """

    def __init__(self):
        """Initialize validator."""
        self.results = {
            "completeness": ValidationResult("completeness"),
            "format": ValidationResult("format"),
            "ranges": ValidationResult("ranges"),
            "alignment": ValidationResult("alignment")
        }

    def validate_completeness(self, df: pd.DataFrame, filename: str) -> None:
        """
        Check for missing dates in quarterly sequence.

        Args:
            df: DataFrame with 'date' column
            filename: Name of file being validated
        """
        if len(df) == 0:
            self.results["completeness"].add_issue(
                f"{filename}: No data found"
            )
            return

        # Check for at least 2 observations
        if len(df) < 2:
            self.results["completeness"].add_issue(
                f"{filename}: Insufficient data (need at least 2 quarters)"
            )
            return

        # Generate expected quarterly dates
        start_date = df["date"].min()
        end_date = df["date"].max()

        expected_dates = pd.date_range(
            start=start_date,
            end=end_date,
            freq="QE"
        )

        # Check for gaps
        df_dates = set(df["date"].dt.to_period("Q"))
        expected_periods = set(expected_dates.to_period("Q"))

        missing = expected_periods - df_dates
        if missing:
            missing_str = sorted([str(p) for p in missing])
            self.results["completeness"].add_issue(
                f"{filename}: Missing quarters: {', '.join(missing_str[:5])}"
                + (f" and {len(missing) - 5} more" if len(missing) > 5 else "")
            )

    def validate_format(self, df: pd.DataFrame, filename: str) -> None:
        """
        Verify date format and chronological ordering.

        Args:
            df: DataFrame with 'date' column
            filename: Name of file being validated
        """
        # Check if dates are properly parsed
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            self.results["format"].add_issue(
                f"{filename}: Date column is not datetime type"
            )
            return

        # Check chronological ordering
        if not df["date"].is_monotonic_increasing:
            self.results["format"].add_issue(
                f"{filename}: Dates are not in chronological order"
            )

        # Check for duplicate dates
        duplicates = df["date"].duplicated().sum()
        if duplicates > 0:
            self.results["format"].add_issue(
                f"{filename}: Found {duplicates} duplicate dates"
            )

    def validate_ranges(self, df: pd.DataFrame, filename: str) -> None:
        """
        Check if values are within economically reasonable ranges.

        Args:
            df: DataFrame with 'value' column
            filename: Name of file being validated
        """
        if filename not in VALUE_RANGES:
            return

        config = VALUE_RANGES[filename]
        min_val = config["min"]
        max_val = config["max"]
        series_name = config["name"]

        # Check for values outside range
        out_of_range = df[
            (df["value"] < min_val) | (df["value"] > max_val)
        ]

        if len(out_of_range) > 0:
            extreme_vals = out_of_range["value"].tolist()[:3]
            self.results["ranges"].add_issue(
                f"{filename} ({series_name}): {len(out_of_range)} values "
                f"outside reasonable range [{min_val}, {max_val}]. "
                f"Examples: {extreme_vals}"
            )

        # Check for NaN values
        nan_count = df["value"].isna().sum()
        if nan_count > 0:
            self.results["ranges"].add_issue(
                f"{filename}: Found {nan_count} missing values (NaN)"
            )

    def validate_alignment(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """
        Verify all series cover the same time period.

        Args:
            dataframes: Dict mapping filenames to DataFrames
        """
        if len(dataframes) < 2:
            return

        # Get date ranges for each series
        date_ranges = {}
        for filename, df in dataframes.items():
            if len(df) > 0:
                date_ranges[filename] = (
                    df["date"].min(),
                    df["date"].max()
                )

        # Check if all series have overlapping periods
        all_starts = [start for start, _ in date_ranges.values()]
        all_ends = [end for _, end in date_ranges.values()]

        latest_start = max(all_starts)
        earliest_end = min(all_ends)

        if latest_start > earliest_end:
            self.results["alignment"].add_issue(
                "Time series do not overlap. Date ranges: " +
                ", ".join([
                    f"{fn}: {start.date()} to {end.date()}"
                    for fn, (start, end) in date_ranges.items()
                ])
            )

        # Check if date ranges are significantly different
        start_range = max(all_starts) - min(all_starts)
        end_range = max(all_ends) - min(all_ends)

        if start_range > timedelta(days=365):
            self.results["alignment"].add_issue(
                f"Series start dates differ by {start_range.days} days"
            )

        if end_range > timedelta(days=365):
            self.results["alignment"].add_issue(
                f"Series end dates differ by {end_range.days} days"
            )

    def run_validation(self) -> Tuple[bool, Dict]:
        """
        Run all validation checks on raw data files.

        Returns:
            Tuple of (all_passed: bool, report: dict)
        """
        # Load all data files
        dataframes = {}
        for filename in VALUE_RANGES.keys():
            file_path = DATA_RAW_DIR / filename

            if not file_path.exists():
                self.results["completeness"].add_issue(
                    f"File not found: {filename}"
                )
                continue

            try:
                df = pd.read_csv(file_path)
                df["date"] = pd.to_datetime(df["date"])
                dataframes[filename] = df

                # Run individual checks
                self.validate_completeness(df, filename)
                self.validate_format(df, filename)
                self.validate_ranges(df, filename)

            except Exception as e:
                self.results["format"].add_issue(
                    f"{filename}: Failed to load - {str(e)}"
                )

        # Run alignment check across all series
        self.validate_alignment(dataframes)

        # Determine overall status
        all_passed = all(
            result.passed for result in self.results.values()
        )

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "PASS" if all_passed else "FAIL",
            "checks": {
                name: result.to_dict()
                for name, result in self.results.items()
            },
            "summary": self._generate_summary()
        }

        # If validation passed, copy files to validated directory
        if all_passed:
            self._copy_validated_files(dataframes)

        return all_passed, report

    def _generate_summary(self) -> str:
        """Generate human-readable summary of validation results."""
        failed_checks = [
            name for name, result in self.results.items()
            if not result.passed
        ]

        if not failed_checks:
            return "All validation checks passed. Data is ready for analysis."
        else:
            return (
                f"Validation failed. {len(failed_checks)} check(s) failed: "
                f"{', '.join(failed_checks)}. See 'checks' for details."
            )

    def _copy_validated_files(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """
        Copy validated files to validated directory.

        Args:
            dataframes: Dict of validated DataFrames
        """
        DATA_VALIDATED_DIR.mkdir(parents=True, exist_ok=True)

        for filename, df in dataframes.items():
            output_path = DATA_VALIDATED_DIR / filename
            df.to_csv(output_path, index=False)


def main():
    """
    Main entry point for validation sub-agent.

    This sub-agent can be invoked independently:
        python agents/validator.py

    Or as part of the main pipeline orchestration.
    """
    # Create outputs directory
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Run validation
    validator = DataValidator()
    passed, report = validator.run_validation()

    # Save report
    report_path = OUTPUTS_DIR / "validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, indent=2, fp=f)

    # Exit with appropriate code
    if passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
