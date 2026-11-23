import json
from pathlib import Path
from typing import Any

if __package__:
    from .fd001_sensors import sensors
else:
    from fd001_sensors import sensors

SCHEMA_VERSION = "1.0"  # Format of JSON
VALID_STATUSES = {"not_evaluated", "candidate", "supported", "rejected"}  # Represents relationship's lifecycle.

def measurement_details(measurement_key: str) -> dict[str, str]:
    """
    Returns a safe, consistent metadata record for one FD001 measurement.
    """

    # Checks whether the selected key exists in the shared sensor dictionary.
    if measurement_key not in sensors:
        available = ", ".join(sorted(sensors))
        raise ValueError(
            f"Unknown FD001 measurement: {measurement_key}. "
            f"Choose one of: {available}"
        )
    
    # Obtains dictionary associated with the measurement.
    details = sensors[measurement_key]
    return {
        "key": measurement_key,
        "symbol": details["symbol"],
        "name": details["name"],
        "component": details["component"],
        "unit": details["unit"]
    }

def build_fd001_causal_inquiry(
        candidate_source: str = "hpc_exit_total_pressure",
        target: str = "hpc_exit_temperature"
) -> dict[str, Any]:
    """
    Builds an unevaluated causal question for the Neo4j integration prototype.
    """

    # Prevents a relationship with self.
    if candidate_source == target:
        raise ValueError(
            "The candidate source and target must be different measurements."
        )
    
    source_details = measurement_details(candidate_source)
    target_details = measurement_details(target)

    inquiry = {
        "schema_version": SCHEMA_VERSION,
        "inquiry_id": (
            f"FD001-{source_details['symbol']}-{target_details['symbol']}-001"
        ),
        "question": (
            f"Does a change in {source_details['name']} "
            f"({source_details['symbol']}) have a defensible causal effect on "
            f"{target_details['name']} ({target_details['symbol']}) during the "
            "documented FD001 HPC degradation scenario?"
        ),
        "dataset": {
            "name": "NASA C-MAPSS",
            "subset": "FD001",
            "fault_mode": "HPC degradation",
            "source_url": (
                "https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data"
            ),
        },
        "candidate_source": source_details,
        "target": target_details,
        "selection_reason": (
            "Both measurements are documented FD001 readings associated with the "
            "HPC component. They are used to test the integration contract, not to "
            "assert that one physically causes the other."
        ),
        "analysis": {
            "status": "not_evaluated",
            "causal_direction_established": False,
            "method": None,
            "effect_estimate": None,
            "counterfactual_answer": None
        },
        "evidence": [
            {
                "evidence_id": "NASA-CMAPSS-FD001",
                "evidence_type": "dataset_documentation",
                "source_title": "C-MAPSS Jet Engine Simulated Data",
                "source_url": (
                    "https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data"
                ),
                "supports": (
                    "FD001 contains one documented HPC degradation fault mode."
                )
            },
            {
                "evidence_id": "NASA-CMAPSS-SENSOR-TABLE",
                "evidence_type": "variable_definition",
                "source_title": (
                    "Damage Propagation Modeling for Aircraft Engine "
                    "Run-to-Failure Simulation"
                ),
                "source_url": (
                    "https://data.nasa.gov/dataset/damage-propagation-modeling-"
                    "for-aircraft-engine-run-to-failure-simulation"
                ),
                "supports": (
                    "P30 and T30 are documented C-MAPSS measurements."
                )
            }
        ],
        "assumptions": [
            (
                "The metadata in fd001_sensors.py accurately represents the cited "
                "NASA sensor definitions."
            ),
            (
                "The source and target roles are prototype inputs and do not "
                "establish a causal direction."
            )
        ],
        "limitations": [
            "No causal discovery or causal inference method has been executed.",
            "Sensor measurements are observations, not physical interventions.",
            "The temporal and multi engine structure of FD001 is not modeled here.",
            "This inquiry cannot support a maintenance recommendation."
        ]
    }

    validate_causal_inquiry(inquiry)  # Passes dictionary containing causal inquiry record to function.
    return inquiry

def validate_causal_inquiry(inquiry: dict[str, Any]) -> None:
    """
    Rejects incomplete or misleading inquiry records before integration.
    """

    required_fields = {
        "schema_version",
        "inquiry_id",
        "question",
        "dataset",
        "candidate_source",
        "target",
        "selection_reason",
        "analysis",
        "evidence",
        "assumptions",
        "limitations"
    }

    missing_fields = required_fields - inquiry.keys()

    if missing_fields:
        raise ValueError(
            f"Missing inquiry fields: {sorted(missing_fields)}"
        )
    
    if inquiry["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"Expected schema version {SCHEMA_VERSION}."
        )
    
    for role in ["candidate_source", "target"]:
        required_measurement_fields = {
            "key",
            "symbol",
            "name",
            "component",
            "unit"
        }

        missing_measurement_fields = required_measurement_fields - inquiry[role].keys()

        if missing_measurement_fields:
            raise ValueError(
                f"Missing {role} fields: "
                f"{sorted(missing_measurement_fields)}"
            )
        
    if (inquiry["candidate_source"]["key"] == inquiry["target"]["key"]):
        raise ValueError(
            "The candidate source and target must be different measurements"
        )
    
    analysis = inquiry["analysis"]
    status = analysis.get("status")

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Unknown analysis status: {status}"
        )
    
    if status == "not_evaluated":
        if analysis.get("causal_direction_established") is not False:
            raise ValueError(
                "An unevaluated inquiry cannot establish causal direction."
            )
        
        for field in [
            "method",
            "effect_estimate",
            "counterfactual_answer"
        ]:
            if analysis.get(field) is not None:
                raise ValueError(
                    f"An unevaluated inquiry must leave {field} empty."
                )
            
    if not inquiry["evidence"]:
        raise ValueError(
            "At least one evidence record is required."
        )
    
    if not inquiry["assumptions"]:
        raise ValueError(
            "At least one assumption is required."
        )
    
    if not inquiry["limitations"]:
        raise ValueError(
            "At least one limitation is required."
        )
    
def save_causal_inquiry(
        inquiry: dict[str, Any],
        output_path: str | Path
) -> Path:
    """
    Validates and saves an inquiry as readable JSON for another component.
    """

    validate_causal_inquiry(inquiry)

    output_path = Path(output_path)  # Converts string path into a Path object.
    output_path.parent.mkdir(
        parents = True,
        exist_ok = True
    )

    # Opens file safely.
    with output_path.open(
        "w",
        encoding = "utf-8"
    ) as output_file:
        json.dump(
            inquiry,
            output_file,
            indent = 2,
            ensure_ascii = False
        )
        output_file.write("\n")

    return output_path

if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parent.parent  # Finds project's root directory.

    # Constructs path to example JSON file.
    example_path = (
        repository_root
        / "examples"
        / "fd001_causal_inquiry.json"
    )

    example_inquiry = build_fd001_causal_inquiry()
    saved_path = save_causal_inquiry(
        example_inquiry,
        example_path
    )

    print(f"Saved causal inquiry: {saved_path}")
    print(f"Question: {example_inquiry['question']}")
    print(f"Status: {example_inquiry['analysis']['status']}")
    print("No causal direction or effect has been established.")