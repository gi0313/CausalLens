from pathlib import Path
from rdflib import Graph, Namespace, RDF, Literal, XSD

CAUSALLENS = Namespace(
    "http://www.semanticweb.org/zainabalemara/ontologies/2026/9/untitled-ontology-3/"
)

ONTOLOGY_FILE = Path(__file__).resolve().parent.parent / "ontology/CausalLens.ttl"


def load_ontology():
    graph = Graph()
    graph.parse(ONTOLOGY_FILE, format="turtle")
    return graph


def map_engine(engine_data):
    graph = load_ontology()

    engine_id = int(engine_data.iloc[0]["engine_id"])

    engine = CAUSALLENS[f"Engine_{engine_id}"]
    run = CAUSALLENS[f"Run_{engine_id}"]

    graph.add((engine, RDF.type, CAUSALLENS.Engine))
    graph.add((run, RDF.type, CAUSALLENS.EngineRun))
    graph.add((engine, CAUSALLENS.hasRun, run))

    for _, row in engine_data.iterrows():
        cycle_number = int(row["cycle"])

        cycle = CAUSALLENS[f"Engine_{engine_id}_Cycle_{cycle_number}"]

        graph.add((cycle, RDF.type, CAUSALLENS.CycleRecord))
        graph.add((run, CAUSALLENS.hasCycle, cycle))
        graph.add(
            (cycle, CAUSALLENS.cycleNumber,
             Literal(cycle_number, datatype=XSD.integer))
        )

        sensor = CAUSALLENS["Sensor_2"]
        reading = CAUSALLENS[
            f"Engine_{engine_id}_Cycle_{cycle_number}_Sensor_2_Reading"
        ]

        graph.add((sensor, RDF.type, CAUSALLENS.Sensor))
        graph.add((reading, RDF.type, CAUSALLENS.SensorReading))
        graph.add((cycle, CAUSALLENS.hasReading, reading))
        graph.add((reading, CAUSALLENS.measuredBy, sensor))
        graph.add(
            (reading, CAUSALLENS.sensorValue,
             Literal(float(row["sensor_2"]), datatype=XSD.double))
        )

    return graph