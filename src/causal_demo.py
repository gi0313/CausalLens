"""
Run the complete CausalLens causal diagnostic prototype.
This demonstration integrates:
1. The existing FD001 loader
2. The documented diagnostic graph
3. The prototype diagnostic calculation
4. Graph path explanations
5. Provenance recording
6. Reusable, CSV, PNG, and JSON outputs
"""

from __future__ import annotations

from pathlib import Path
import json

from causal_graph import (
    build_causal_graph,
    save_graph_image,
    validate_graph_metadata
)

from causal_provenance import create_provenance_record

from diagnostic_query import (
    calculate_diagnostic_indicator,
    save_indicator_plot,
    summarize_diagnostic
)

from fd001_loader import get_engine, load_fd001

# __file__ refers to this script.
# parents[1] moves from the src folder to the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "train_FD001.txt"
)

EDGE_REGISTER_PATH = (
    PROJECT_ROOT
    / "docs"
    / "causal_edge_register.csv"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "exports"
    / "causal_demo"
)

# Engine 1 provides a repeatable initial demonstration. A future interface can allow the user to choose the engine dynamically.
SELECTED_ENGINE_ID = 1

def main() -> None:
    """
    Run the complete demonstration and save its evidence artifacts.
    """

    print("1. Loading and validating FD001 training data...")

    # Reuse the team's existing loader
    fd001_data = load_fd001(
        DATASET_PATH,
        split = "train"
    )

    print(f" Loaded {len(fd001_data):,} cycle records.")

    print(f"2. Selecting engine {SELECTED_ENGINE_ID}...")

    engine_data = get_engine(
        fd001_data,
        SELECTED_ENGINE_ID
    )

    print(f" Selected {len(engine_data):,} cycles.")

    print("3. Building the documented diagnostic graph...")

    graph = build_causal_graph(EDGE_REGISTER_PATH)
    validate_graph_metadata(graph)

    print(
        f" Graph contains {graph.number_of_nodes()} nodes "
        f"and {graph.number_of_edges()} edges."
    )

    print("4. Calculating the diagnostic indicator...")

    analyzed_data, threshold = (calculate_diagnostic_indicator(engine_data))

    print(f" Exploratory threshold: {threshold: .3f}")

    print("5. Creating the result and provenance record...")

    diagnostic_summary = summarize_diagnostic(
        analyzed_data,
        threshold,
        graph
    )

    provenance = create_provenance_record(
        dataset_path = DATASET_PATH,
        engine_id = SELECTED_ENGINE_ID,
        threshold = threshold,
        graph = graph
    )

    # Create the output folder if it does not already exist.
    OUTPUT_DIRECTORY.mkdir(
        parents = True,
        exist_ok = True
    )

    analyzed_csv_path = (OUTPUT_DIRECTORY / "analyzed_engine.csv")

    graph_image_path = (OUTPUT_DIRECTORY / "diagnostic_graph.png")

    indicator_image_path = (OUTPUT_DIRECTORY / "diagnostic_indicator.png")

    result_json_path = (OUTPUT_DIRECTORY / "diagnostic_result.json")

    print("6. Saving demonstration outputs...")

    analyzed_data.to_csv(
        analyzed_csv_path,
        index = False
    )

    save_graph_image(
        graph,
        graph_image_path
    )

    save_indicator_plot(
        analyzed_data,
        threshold,
        str(indicator_image_path)
    )

    output_record = {
        "diagnostic_summary": diagnostic_summary,
        "provenance": provenance
    }

    with result_json_path.open(
        "w",
        encoding = "utf-8"
    ) as output_file:
        json.dump(
            output_record,
            output_file,
            indent = 2,
            allow_nan = False
        )

    print("\nDemonstration completed successfully.")
    print(f"Analyzed data: {analyzed_csv_path}")
    print(f"Graph image: {graph_image_path}")
    print(f"Indicator image: {indicator_image_path}")
    print(f"Result and provenance: {result_json_path}")

    print(
        "\nReminder: This is an exploratory prototype and not "
        "a validated maintenance recommendation."
    )

if __name__ == "__main__":
    # This prevents the demonstration from running automatically if another Python module imports functions from this file.
    main()