from pathlib import Path
from rdflib import Graph, Namespace, RDF, Literal, XSD

try:
    from .fd001_loader import get_observations
except ImportError:
    from fd001_loader import get_observations

CAUSALLENS = Namespace(
    "http://www.semanticweb.org/zainabalemara/ontologies/2026/9/untitled-ontology-3/"
)

ONTOLOGY_FILE = Path(__file__).resolve().parent.parent / "ontology/CausalLens.ttl"


def load_ontology():
    graph = Graph()
    graph.parse(ONTOLOGY_FILE, format="turtle")
    return graph


def map_engine(engine_data, measurement="lpc_exit_temperature"):
    graph = load_ontology()

    engine_id = int(engine_data.iloc[0]["engine_id"])
    dataset = engine_data.iloc[0]["dataset"]
    split = engine_data.iloc[0]["split"]

    engine = CAUSALLENS[f"{dataset}_{split}_Engine_{engine_id}"]
    run = CAUSALLENS[f"{dataset}_{split}_Run_{engine_id}"]

    graph.add((engine, RDF.type, CAUSALLENS.Engine))
    graph.add((run, RDF.type, CAUSALLENS.EngineRun))
    graph.add((engine, CAUSALLENS.hasRun, run))

    observations = get_observations(engine_data)

    observations = observations[
        observations["measurement"] == measurement
    ]

    for _, row in observations.iterrows():
        cycle_number = int(row["cycle"])
        symbol = row["symbol"]

        cycle = CAUSALLENS[
            f"{dataset}_{split}_Engine_{engine_id}_Cycle_{cycle_number}"
        ]

        graph.add((cycle, RDF.type, CAUSALLENS.CycleRecord))
        graph.add((run, CAUSALLENS.hasCycle, cycle))

        graph.add(
            (
                cycle,
                CAUSALLENS.cycleNumber,
                Literal(cycle_number, datatype=XSD.integer),
            )
        )

        sensor = CAUSALLENS[f"Sensor_{symbol}"]

        reading = CAUSALLENS[
            f"{dataset}_{split}_Engine_{engine_id}"
            f"_Cycle_{cycle_number}_{symbol}_Reading"
        ]

        graph.add((sensor, RDF.type, CAUSALLENS.Sensor))

        graph.add(
            (
                sensor,
                CAUSALLENS.sensorCode,
                Literal(symbol),
            )
        )

        graph.add((reading, RDF.type, CAUSALLENS.SensorReading))
        graph.add((cycle, CAUSALLENS.hasReading, reading))
        graph.add((reading, CAUSALLENS.measuredBy, sensor))

        graph.add(
            (
                reading,
                CAUSALLENS.sensorValue,
                Literal(float(row["value"]), datatype=XSD.double),
            )
        )

    return graph