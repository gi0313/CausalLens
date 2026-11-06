"""
Automated tests for the CausalLens causal diagnostic prototype.
The tests use a small, controlled dataset so they run quickly. The actual demonstration uses the real NASA C-MAPSS FD001 dataset.
"""

from pathlib import Path

import json
import networkx as nx
import pandas as pd
import pytest

from causal_graph import (
    build_causal_graph,
    validate_graph_metadata
)
from diagnostic_query import (
    calculate_diagnostic_indicator,
    find_diagnostic_paths,
    summarize_diagnostic
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EDGE_REGISTER = (
    PROJECT_ROOT
    / "docs"
    / "causal_edge_register.csv"
)

@pytest.fixture
def graph() -> nx.DiGraph:
    """
    Create a fresh diagnostic graph for each applicable test.
    """

    return build_causal_graph(EDGE_REGISTER)

@pytest.fixture
def sample_engine_data() -> pd.DataFrame:
    """
    Create a small single engine dataset using real project column names.
    These simple values test the software. They are not intended to reproduce realistic turbofan engine physics.
    """

    return pd.DataFrame(
        {
            "engine_id": [1] * 10,
            "cycle": list(range(1, 11)),
            "hpc_exit_static_pressure": [
                47.0,
                47.1,
                46.9,
                47.0,
                47.2,
                47.8,
                48.3,
                49.0,
                50.0,
                51.5
            ],
            "fuel_flow_per_hpc_static_pressure": [
                0.520,
                0.521,
                0.519,
                0.520,
                0.522,
                0.528,
                0.535,
                0.544,
                0.556,
                0.570
            ],
            "bypass_ratio": [
                8.40,
                8.41,
                8.39,
                8.40,
                8.42,
                8.35,
                8.29,
                8.22,
                8.14,
                8.05
            ]
            
        }
    )

def test_graph_is_directed_and_acyclic(graph: nx.DiGraph) -> None:
    """
    Confirm the graph is directed and contains no feedback loops.
    """

    assert graph.is_directed()
    assert nx.is_directed_acyclic_graph(graph)

def test_every_edge_has_provenance_metadata(graph: nx.DiGraph) -> None:
    """
    Confirm every edge documents its basis, source, and limitation.
    """

    validate_graph_metadata(graph)

    for _, _, attributes in graph.edges(data = True):
        assert attributes["description"]
        assert attributes["evidence_basis"]
        assert attributes["source_reference"]
        assert attributes["limitation"]
        assert isinstance(attributes["validated"], bool)

def test_diagnostic_indicator_is_created(sample_engine_data: pd.DataFrame) -> None:
    """
    Confirm the calculation creates the expected analysis fields.
    """

    analyzed, threshold = calculate_diagnostic_indicator(sample_engine_data)

    assert "degradation_indicator" in analyzed.columns
    assert "elevated_condition" in analyzed.columns
    assert len(analyzed) == len(sample_engine_data)
    assert threshold >= 0
    assert analyzed["elevated_condition"].any()

def test_supported_measurements_have_paths(graph: nx.DiGraph) -> None:
    """
    Confirm all three supported measurements reach the diagnostic outcome.
    """

    paths = find_diagnostic_paths(graph)

    assert len(paths) == 3

    for path in paths:
        assert path[-1] == "elevated_condition"
        assert "degradation_indicator" in path

def test_unsupported_target_is_rejected(graph: nx.DiGraph) -> None:
    """
    Confirm an unknown target produces a clear error.
    """

    with pytest.raises(
        ValueError,
        match = "Unsupported diagnostic target"
    ):
        find_diagnostic_paths(
            graph,
            target = "unknown_failure"
        )

def test_summary_can_be_converted_to_json(
    sample_engine_data: pd.DataFrame,
    graph: nx.DiGraph
) -> None:
    """
    Confirm the result can be transferred to other system components.
    """

    analyzed, threshold = calculate_diagnostic_indicator(sample_engine_data)

    summary = summarize_diagnostic(
        analyzed,
        threshold,
        graph
    )

    json_text = json.dumps(
        summary,
        allow_nan = False
    )

    assert '"engine_id": 1' in json_text
    assert "diagnostic_paths" in summary
    assert "limitation" in summary

