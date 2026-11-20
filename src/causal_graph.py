"""
Build and validate the prototype CausalLens diagnostic graph.
The graph is loaded from a separate edge register so every relationship has a documented basis, source, validation status, and limitation.
A directed path in this prototype does not automatically prove a physical causal relationship. Some edges represent prototype assumptions,
while other edges represent mathematical calculation dependencies.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

# These are actual FD001 measurements used as inputs to the prototype.
ANALYSIS_INPUT_NODES = {
    "hpc_exit_static_pressure",
    "fuel_flow_per_hpc_static_pressure",
    "bypass_ratio"
}

# Human readable labels make the technical graph nodes easier to explain
NODE_LABELS = {
    "cycle_fraction": "Progress Through Engine Run",
    "hpc_exit_static_pressure": "HPC Exit Static Pressure",
    "fuel_flow_per_hpc_static_pressure": "Fuel Flow / HPC Pressure",
    "bypass_ratio": "Bypass Ratio",
    "degradation_indicator": "Prototype Degradation Indicator",
    "elevated_condition": "Elevated Diagnostic Condition"
}

def text_to_boolean(value: object) -> bool:
    """
    Convert a CSV value into a Python Boolean.
    CSV files store values as text. This function accepts common true values such as 'true', 'yes', and '1'. All other values are treated as False.
    """

    return str(value).strip().lower() in {"true", "yes", "1"}

def load_edge_register(register_path: str | Path) -> pd.DataFrame:
    """
    Load and validate the causal edge register.
    Parameters:
        register_path: Location of the CSV file containing the graph relationships.
        
    Returns:
        pandas.DataFrame: Validated edge records.
        
    Raises:
    FileNotFoundError: Raised when the register cannot be found.
    ValueError: Raised when required columns or values are missing.
    """

    register_path = Path(register_path)

    if not register_path.exists():
        raise FileNotFoundError(f"Edge register was not found: {register_path}")
    
    edge_data = pd.read_csv(register_path)

    # These fields are required so that no relationship is undocumented.
    required_columns = {"source", "target", "relation_type", "description", "evidence_basis", "source_reference", "validated", "limitation"}

    missing_columns = required_columns - set(edge_data.columns)

    if missing_columns:
        raise ValueError(
            "The edge register is missing required columns: "
            f"{sorted(missing_columns)}"
        )
    
    # Empty documentation would make the graph difficult to audit.
    if edge_data[list(required_columns)].isna().any().any():
        raise ValueError("The edge register contains blank required values.")
    
    return edge_data

def build_causal_graph(register_path: str | Path) -> nx.DiGraph:
    """
    Build a directed graph using the documented edge register.
    A directed edge A -> B means the prototype represents information moving or contributing from A to B. It does not automatically mean A physically causes B.
    """

    edge_data = load_edge_register(register_path)
    graph = nx.DiGraph()

    for edge in edge_data.itertuples(index = False):
        # Add each relationship and preserve all supporting documentation as edge attributes.
        graph.add_edge(
            edge.source,
            edge.target,
            relation_type = edge.relation_type,
            description = edge.description,
            evidence_basis = edge.evidence_basis,
            source_reference = edge.source_reference,
            validated = text_to_boolean(edge.validated),
            limitation = edge.limitation
        )

    # A directed acyclic graph cannot contain a path that loops back to its starting point. Cycles could make a diagnostic explanation confusing.
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("The diagnostic graph contains a directed cycle.")
    
    return graph

def validate_graph_metadata(graph: nx.DiGraph) -> None:
    """
    Confirm that every edge includes its required provenance information.
    """
    
    required_attributes = {"relation_type", "description", "evidence_basis", "source_reference", "validated", "limitation"}

    for source, target, attributes in graph.edges(data = True):
        missing = required_attributes - set(attributes)

        if missing:
            raise ValueError(f"Edge {source} -> {target} is missing: {sorted(missing)}")
        
def save_graph_image(
    graph: nx.DiGraph,
    output_path: str | Path,
) -> Path:
    """
    Save a simple, readable diagram of the diagnostic calculation.

    Rounded boxes and short multiline labels are used instead of circular
    nodes because the graph contains long technical measurement names.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # These fixed positions produce three clear columns:
    # FD001 measurements -> calculated indicator -> diagnostic result.
    positions = {
        "hpc_exit_static_pressure": (0, 2),
        "fuel_flow_per_hpc_static_pressure": (0, 1),
        "bypass_ratio": (0, 0),
        "degradation_indicator": (2.2, 1),
        "elevated_condition": (4.4, 1),
    }

    # Short multiline labels fit inside boxes better than the original labels.
    display_labels = {
        "hpc_exit_static_pressure": "HPC Exit\nStatic Pressure",
        "fuel_flow_per_hpc_static_pressure": (
            "Fuel Flow /\nHPC Pressure"
        ),
        "bypass_ratio": "Bypass\nRatio",
        "degradation_indicator": (
            "Prototype\nDegradation Indicator"
        ),
        "elevated_condition": (
            "Elevated\nDiagnostic Condition"
        ),
    }

    figure, axis = plt.subplots(figsize=(12, 6))

    # Draw arrows first so the boxes and their text remain on top.
    for source, target in graph.edges:
        if source not in positions or target not in positions:
            continue

        axis.annotate(
            "",
            xy=positions[target],
            xytext=positions[source],
            arrowprops={
                "arrowstyle": "-|>",
                "color": "#444444",
                "linewidth": 1.8,
                "mutation_scale": 18,
                "shrinkA": 55,
                "shrinkB": 55,
            },
        )

    # Draw every node as a rounded text box.
    for node in graph.nodes:
        if node not in positions:
            continue

        if node in ANALYSIS_INPUT_NODES:
            box_color = "#DCEAF7"
        elif node == "degradation_indicator":
            box_color = "#E8E8E8"
        else:
            box_color = "#F3DADA"

        x_position, y_position = positions[node]

        axis.text(
            x_position,
            y_position,
            display_labels.get(node, node),
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=10,
            bbox={
                "boxstyle": "round,pad=0.65",
                "facecolor": box_color,
                "edgecolor": "#333333",
                "linewidth": 1.3,
            },
        )

    # Label the three stages so a non-expert can understand the workflow.
    axis.text(
        0,
        2.55,
        "FD001 Measurements",
        horizontalalignment="center",
        fontsize=11,
        fontweight="bold",
    )

    axis.text(
        2.2,
        2.55,
        "Prototype Calculation",
        horizontalalignment="center",
        fontsize=11,
        fontweight="bold",
    )

    axis.text(
        4.4,
        2.55,
        "Diagnostic Output",
        horizontalalignment="center",
        fontsize=11,
        fontweight="bold",
    )

    axis.set_title(
        "CausalLens Prototype Diagnostic Dependency Graph\n"
        "Calculation flow—not validated physical causation",
        fontsize=14,
        pad=20,
    )

    axis.set_xlim(-1, 5.3)
    axis.set_ylim(-0.7, 2.9)
    axis.axis("off")

    plt.tight_layout()
    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(figure)

    return output_path