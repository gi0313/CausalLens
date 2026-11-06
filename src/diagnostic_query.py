"""
Calculate a prototype engine diagnostic indicator and query graph paths.
This module uses real FD001 measurements, but its threshold and causal relationships are exploratory. Results must not be treated as validated maintenance recommendations.
"""

from __future__ import annotations
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

# These measurement names come from the project's FD001 sensor dictionary.
ANALYSIS_MEASUREMENTS = ["hpc_exit_static_pressure", "fuel_flow_per_hpc_static_pressure", "bypass_ratio"]

def validate_engine_data(engine_data: pd.DataFrame) -> None:
    """
    Confirm that one engine's data contains the fields needed for analysis.
    """

    required_columns = {"engine_id", "cycle", *ANALYSIS_MEASUREMENTS}
    missing_columns = required_columns - set(engine_data.columns)

    if missing_columns:
        raise ValueError(
            "Engine data is missing required columns: "
            f"{sorted(missing_columns)}"
        )
    
    if engine_data.empty:
        raise ValueError("The selected engine contains no cycle records.")
    
    # A diagnostic trajectory must represent only one engine.
    if engine_data["engine_id"].nunique() != 1:
        raise ValueError("Diagnostic analysis requires data for exactly one engine.")
    
    if engine_data[list(ANALYSIS_MEASUREMENTS)].isna().any().any():
        raise ValueError("The selected measurements contain missing values.")
    
def calculate_diagnostic_indicator(
    engine_data: pd.DataFrame,
    baseline_fraction: float = 0.20,
    threshold_quantile: float = 0.90
) -> tuple[pd.DataFrame, float]:
    """
    Calculate a prototype degradation indicator for one engine.
    Method:
    1. Sort the engine's records by cycle.
    2. Treat the earliest 20 percent of cycles as an exploratory baseline.
    3. Calculate the baseline mean and standard deviation for each sensor.
    4. Measure each cycle's absolute standardized deviation from the baseline.
    5. Average the three deviations to obtain one diagnostic indicator.
    6. Use the engine's 90th percentile as an exploratory elevated threshold.

    The baseline and threshold are prototype choices. They have not been validated as engineering or maintenance limits.
    """

    validate_engine_data(engine_data)

    if not 0 < baseline_fraction <= 1:
        raise ValueError("baseline_fraction must be greater than 0 and at most 1.")
    
    if not 0 < threshold_quantile < 1:
        raise ValueError("threshold_quantile must be between 0 and 1.")
    
    # Work on a copy so the caller's original DataFrame is not changed.
    result = engine_data.copy().sort_values("cycle").reset_index(drop = True)

    total_cycles = len(result)

    # Use at least five cycles when possible so the baseline is not calculated from only one or two observations.
    baseline_count = max(5, int(np.ceil(total_cycles * baseline_fraction)))
    baseline_count = min(baseline_count, total_cycles)

    baseline = result.iloc[:baseline_count]

    # Express the current cycle as a fraction of the selected engine's run. This provides a normalized progress value from approximately 0 to 1.
    maximum_cycle = result["cycle"].max()
    result["cycle_fraction"] = result["cycle"] / maximum_cycle

    deviation_columns: list[str] = []

    for measurement in ANALYSIS_MEASUREMENTS:
        baseline_mean = baseline[measurement].mean()
        baseline_standard_deviation = baseline[measurement].std(ddof = 0)

        # A standard deviation of zero would cause division by zero. If a measurement is constant in the baseline, use a very small denominator.
        safe_standard_deviation = max(float(baseline_standard_deviation), 1e-9)

        deviation_column = f"{measurement}_absolute_z"

        # Absolute standardized deviation describes how far a measurement is from its early operation baseline, regardless of direction.
        result[deviation_column] = (
            (result[measurement] - baseline_mean).abs()
            / safe_standard_deviation
        )

        deviation_columns.append(deviation_column)
    
    # Average the three devations so the demonstration has one interpretable summary value for each cycle.
    result["degradation_indicator"] = result[deviation_columns].mean(axis = 1)

    # The 90th percentile identifies the highest 10 percent of indicator values for this particular engine. It is only an exploratory prototype threshold.
    threshold = float(result["degradation_indicator"].quantile(threshold_quantile))

    result["elevated_condition"] = (result["degradation_indicator"] >= threshold)

    return result, threshold

def find_diagnostic_paths(
    graph: nx.DiGraph,
    source_measurements: list[str] | None = None,
    target: str = "elevated_condition"
) -> list[list[str]]:
    """
    Find directed explanation paths from measurements to a target node.
    The returned paths explain how the prototype's information and calculations connect. They do not independently prove real world physical causation.
    """

    if source_measurements is None:
        source_measurements = ANALYSIS_MEASUREMENTS
    
    if target not in graph:
        raise ValueError(f"Unsupported diagnostic target: {target}")
    
    paths: list[list[str]] = []

    for source in source_measurements:
        if source not in graph:
            raise ValueError(f"Measurement is not represented in the graph: {source}")
        
        if nx.has_path(graph, source, target):
            paths.extend(
                list(nx.all_simple_paths(graph, source, target)))
    
    return paths

def summarize_diagnostic(
    analyzed_data: pd.DataFrame,
    threshold: float,
    graph: nx.DiGraph
) -> dict[str, Any]:
    """
    Create a JSON compatible diagnostic summary for the selected engine.
    """

    if analyzed_data.empty:
        raise ValueError("Analyzed engine data cannot be empty.")
    
    engine_id = int(analyzed_data["engine_id"].iloc[0])

    peak_index = analyzed_data["degradation_indicator"].idxmax()
    peak_record = analyzed_data.loc[peak_index]

    elevated_records = analyzed_data[analyzed_data["elevated_condition"]]

    first_elevated_cycle = None

    if not elevated_records.empty:
        first_elevated_cycle = int(elevated_records["cycle"].iloc[0])

    diagnostic_paths = find_diagnostic_paths(graph)

    return {
        "engine_id": engine_id,
        "cycle_count": int(len(analyzed_data)),
        "prototype_threshold": float(threshold),
        "peak_indicator": float(peak_record["degradation_indicator"]),
        "peak_indicator_cycle": int(peak_record["cycle"]),
        "first_elevated_cycle": first_elevated_cycle,
        "elevated_cycle_count": int(analyzed_data["elevated_condition"].sum()),
        "measurements": list(ANALYSIS_MEASUREMENTS),
        "diagnostic_paths": diagnostic_paths,
        "interpretation": (
            "The result identifies cycles whose combined sensor deviation is "
            "high relative to this engine's early operation baseline."
        ),
        "limitation": (
            "This exploratory result is not a validated failure prediction, "
            "physical causal conclusion, or maintenance recommendation."
        )
    }

def save_indicator_plot(
    analyzed_data: pd.DataFrame,
    threshold: float,
    output_path: str
) -> None:
    """
    Save the diagnostic indicator over the selected engine's cycles.
    """

    plt.figure(figsize = (12, 6))

    plt.plot(
        analyzed_data["cycle"],
        analyzed_data["degradation_indicator"],
        color = "black",
        label = "Prototype degradation indicator"
    )

    plt.axhline(
        threshold,
        color = "gray",
        linestyle = "--",
        label = "Exploratory 90th percentile threshold"
    )

    elevated = analyzed_data[analyzed_data["elevated_condition"]]

    plt.scatter(
        elevated["cycle"],
        elevated["degradation_indicator"],
        color = "darkred",
        label = "Elevated cycles",
        zorder = 3
    )

    plt.xlabel("Engine Cycle")
    plt.ylabel("Mean Absolute Standardized Deviation")
    plt.title("Prototype FD001 Diagnostic Indicator")
    plt.legend()
    plt.grid(alpha = 0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi = 200, bbox_inches = "tight")
    plt.close()