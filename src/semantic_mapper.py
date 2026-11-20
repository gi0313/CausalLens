from pathlib import Path

from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace

# Support both the VS Code Run button and imports from the repo root.
if __package__:
    from .fd001_loader import get_observations
    from .fd001_sensors import sensors
else:
    from fd001_loader import get_observations
    from fd001_sensors import sensors

CAUSALLENS = Namespace(
    "http://www.semanticweb.org/zainabalemara/ontologies/2026/9/untitled-ontology-3/"
)
ONTOLOGY_FILE = Path(__file__).resolve().parent.parent / "ontology/CausalLens.ttl"


def load_ontology():
    # Read the saved definitions and example individuals into memory.
    return Graph().parse(ONTOLOGY_FILE, format="turtle")


def run_iri(engine_data):
    # The same engine number can appear in different splits.
    first = engine_data.iloc[0]
    return CAUSALLENS[f"{first['dataset']}_{first['split']}_Run_{first['engine_id']}"]


def map_engine(engine_data, measurement="lpc_exit_temperature", *, graph=None):
    # Map one run. Pass measurement=None to include all sensors.
    runs = engine_data[["dataset", "split", "engine_id"]].drop_duplicates()
    if len(runs) != 1:
        raise ValueError("Select one engine from one dataset and split.")
    if measurement is not None and measurement not in sensors:
        raise ValueError(f"Unknown measurement: {measurement}")
    if graph is None:
        graph = load_ontology()

    cl = CAUSALLENS
    run = run_iri(engine_data)
    first = runs.iloc[0]
    dataset = first["dataset"]
    split = first["split"]
    engine_id = int(first["engine_id"])
    engine = cl[f"{dataset}_{split}_Engine_{engine_id}"]
    graph.add((engine, RDF.type, cl.Engine))
    graph.add((run, RDF.type, cl.EngineRun))
    graph.add((engine, cl.hasRun, run))
    graph.add((run, cl.datasetName, Literal(dataset)))
    graph.add((run, cl.datasetSplit, Literal(split)))
    graph.add((run, cl.engineNumber, Literal(engine_id)))

    # Older samples can map readings even if they omit operating settings.
    setting_fields = {
        "altitude": cl.altitude,
        "mach_number": cl.machNumber,
        "throttle_resolver_angle": cl.throttleResolverAngle,
    }
    settings = [name for name in setting_fields if name in engine_data.columns]
    for row in engine_data.itertuples(index=False):
        cycle = cl[row.cycle_id]
        graph.add((cycle, RDF.type, cl.CycleRecord))
        graph.add((run, cl.hasCycle, cycle))
        graph.add((cycle, cl.cycleNumber, Literal(int(row.cycle))))
        if settings:
            condition = cl[f"{row.cycle_id}/settings"]
            graph.add((cycle, cl.hasOperatingCondition, condition))
            graph.add((condition, RDF.type, cl.OperatingCondition))
            for name in settings:
                value = Literal(float(getattr(row, name)), datatype=XSD.double)
                graph.add((condition, setting_fields[name], value))

    # Get values and shared sensor details from the loader.
    observations = get_observations(engine_data)
    if measurement is not None:
        observations = observations[observations["measurement"] == measurement]

    for key, rows in observations.groupby("measurement", sort=False):
        symbol = sensors[key]["symbol"]
        # Reuse the sensor and component links defined in the ontology.
        sensor = graph.value(predicate=cl.sensorCode, object=Literal(symbol), any=False)
        if sensor is None:
            raise ValueError(f"Sensor {symbol} is missing from the ontology.")

        # Each reading links to its cycle and keeps its original ID.
        for row in rows.itertuples(index=False):
            cycle = cl[row.observation_id.rsplit("/", 1)[0]]
            reading = cl[row.observation_id]
            graph.add((reading, RDF.type, cl.SensorReading))
            graph.add((cycle, cl.hasReading, reading))
            graph.add((reading, cl.measuredBy, sensor))
            graph.add((reading, cl.sensorValue, Literal(float(row.value), datatype=XSD.double)))
            graph.add((reading, cl.observationId, Literal(row.observation_id)))
            label = f"{dataset} {split} engine {engine_id} cycle {row.cycle} {symbol}"
            graph.add((reading, RDFS.label, Literal(label)))

    return graph
