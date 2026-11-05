from pathlib import Path
from rdflib import Graph, Namespace, RDF, Literal, XSD

# Import the cleaned sensor observations from the FD001 loader
try:
    from .fd001_loader import get_observations
except ImportError:
    from fd001_loader import get_observations

# Namespace for the CausalLens ontology
CAUSALLENS = Namespace(
    "http://www.semanticweb.org/zainabalemara/ontologies/2026/9/untitled-ontology-3/"
)

# Path to the ontology file
ONTOLOGY_FILE = Path(__file__).resolve().parent.parent / "ontology/CausalLens.ttl"


def load_ontology():
    graph = Graph()
    graph.parse(ONTOLOGY_FILE, format="turtle")
    return graph


def map_engine(engine_data, measurement="lpc_exit_temperature"):
    graph = load_ontology()

    # Get the engine, dataset, and train/test information
    engine_id = int(engine_data.iloc[0]["engine_id"])
    dataset = engine_data.iloc[0]["dataset"]
    split = engine_data.iloc[0]["split"]

    # Create unique identifiers for the engine and its run
    engine = CAUSALLENS[f"{dataset}_{split}_Engine_{engine_id}"]
    run = CAUSALLENS[f"{dataset}_{split}_Run_{engine_id}"]

    # Add the engine and run to the RDF graph
    graph.add((engine, RDF.type, CAUSALLENS.Engine))
    graph.add((run, RDF.type, CAUSALLENS.EngineRun))
    graph.add((engine, CAUSALLENS.hasRun, run))

    # Get the cleaned sensor observations from the loader
    observations = get_observations(engine_data)

    # Keep only the sensor measurement being mapped
    observations = observations[
        observations["measurement"] == measurement
    ]

    # Go through each sensor observation
    for _, row in observations.iterrows():
        cycle_number = int(row["cycle"])
        symbol = row["symbol"]

        # Create a unique identifier for the cycle
        cycle = CAUSALLENS[
            f"{dataset}_{split}_Engine_{engine_id}_Cycle_{cycle_number}"
        ]

        # Add the cycle and connect it to the engine run
        graph.add((cycle, RDF.type, CAUSALLENS.CycleRecord))
        graph.add((run, CAUSALLENS.hasCycle, cycle))

        # Store the cycle number
        graph.add(
            (
                cycle,
                CAUSALLENS.cycleNumber,
                Literal(cycle_number, datatype=XSD.integer),
            )
        )

        # Create the sensor identifier
        sensor = CAUSALLENS[f"Sensor_{symbol}"]

        # Create a unique identifier for the sensor reading
        reading = CAUSALLENS[
            f"{dataset}_{split}_Engine_{engine_id}"
            f"_Cycle_{cycle_number}_{symbol}_Reading"
        ]

        # Add the sensor and its sensor code
        graph.add((sensor, RDF.type, CAUSALLENS.Sensor))

        graph.add(
            (
                sensor,
                CAUSALLENS.sensorCode,
                Literal(symbol),
            )
        )

        # Add the sensor reading and connect it to the cycle and sensor
        graph.add((reading, RDF.type, CAUSALLENS.SensorReading))
        graph.add((cycle, CAUSALLENS.hasReading, reading))
        graph.add((reading, CAUSALLENS.measuredBy, sensor))

        # Store the actual numeric sensor value
        graph.add(
            (
                reading,
                CAUSALLENS.sensorValue,
                Literal(float(row["value"]), datatype=XSD.double),
            )
        )

    return graph