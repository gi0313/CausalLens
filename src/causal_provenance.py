"""
Create provenance records for CausalLens diagnostic demonstrations.
Provenance answers questions such as:
- What dataset file was used?
- Has the file changed?
- Which engine was selected?
- Which code revision produced the result?
- Which software versions were used?
- Which prototype assumptions affected the output?
"""

from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

import hashlib
import platform
import subprocess
from typing import Any
import networkx as nx
import pandas as pd

def calculate_file_sha256(file_path: str | Path) -> str:
    """
    Calculate a SHA 256 fingerprint for a file.
    If a file changes, its fingerprint changes. This helps distinguish between different dataset copies without storing the datasrt in the result.
    """

    file_path = Path(file_path)
    sha256 = hashlib.sha256()

    with file_path.open("rb") as source_file:
        # Read the file in pieces instead of loading it all into memory.
        for chunk in iter(
            lambda: source_file.read(65536),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()

def get_git_commit() -> str | None:
    """
    Return the current Git commit identifier when one is available.
    """

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check = True,
            capture_output = True,
            text = True
        )

        return result.stdout.strip()
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    
def create_provenance_record(
    dataset_path: str | Path,
    engine_id: int,
    threshold: float,
    graph: nx.DiGraph
) -> dict[str, Any]:
    """
    Create a JSON compatible provenance record for one execution.
    """

    dataset_path = Path(dataset_path)
    relationships = []

    for source, target, attributes in graph.edges(data = True):
        relationships.append(
            {
                "source": source,
                "target": target,
                "relation_type": attributes["relation_type"],
                "source_reference": attributes["source_reference"],
                "validated": bool(attributes["validated"]),
                "limitation": attributes["limitation"]
            }
        )

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "name": "NASA C-MAPSS FD001",
            "file": str(dataset_path),
            "sha256": calculate_file_sha256(dataset_path),
            "selected_engine_id": int(engine_id)
        },
        "code": {
            "git_commit": get_git_commit(),
            "working_tree_note": (
                "The Git commit identifies the latest committed "
                "version. Run git status to identify uncommitted changes."
            ),
        },
        "environment": {
            "python_version": platform.python_version(),
            "pandas_version": pd.__version__
        },
        "prototype_configuration": {
            "baseline_fraction": 0.20,
            "threshold_method": ("Engine specific 90th percentile"),
            "threshold_value": float(threshold)
        },
        "relationships": relationships,
        "overall_limitation": (
            "The prototype documents assumptions and calculation "
            "dependencies. It does not establish validated physical "
            "causal relationships."
        )
    }