import pandas as pd

from semantic_mapper import map_engine


sample = pd.DataFrame(
    [
        {
            "dataset": "FD001",
            "split": "train",
            "engine_id": 1,
            "cycle": 1,
            "cycle_id": "FD001/train/engine/1/cycle/1",

            "fan_inlet_temperature": 518.67,
            "lpc_exit_temperature": 642.15,
            "hpc_exit_temperature": 1580.0,
            "lpt_exit_temperature": 1400.0,
            "fan_inlet_pressure": 14.62,
            "bypass_duct_pressure": 21.60,
            "hpc_exit_total_pressure": 554.0,
            "fan_speed": 2388.0,
            "core_speed": 9046.0,
            "engine_pressure_ratio": 1.30,
            "hpc_exit_static_pressure": 47.47,
            "fuel_flow_per_hpc_static_pressure": 521.0,
            "corrected_fan_speed": 2388.0,
            "corrected_core_speed": 8138.0,
            "bypass_ratio": 8.40,
            "burner_fuel_air_ratio": 0.03,
            "bleed_enthalpy": 392.0,
            "requested_fan_speed": 2388.0,
            "requested_corrected_fan_speed": 100.0,
            "hpt_cooling_air_flow": 39.0,
            "lpt_cooling_air_flow": 23.0,
        },
        {
            "dataset": "FD001",
            "split": "train",
            "engine_id": 1,
            "cycle": 2,
            "cycle_id": "FD001/train/engine/1/cycle/2",

            "fan_inlet_temperature": 518.67,
            "lpc_exit_temperature": 643.25,
            "hpc_exit_temperature": 1581.0,
            "lpt_exit_temperature": 1401.0,
            "fan_inlet_pressure": 14.62,
            "bypass_duct_pressure": 21.61,
            "hpc_exit_total_pressure": 555.0,
            "fan_speed": 2389.0,
            "core_speed": 9047.0,
            "engine_pressure_ratio": 1.31,
            "hpc_exit_static_pressure": 47.48,
            "fuel_flow_per_hpc_static_pressure": 522.0,
            "corrected_fan_speed": 2389.0,
            "corrected_core_speed": 8139.0,
            "bypass_ratio": 8.41,
            "burner_fuel_air_ratio": 0.03,
            "bleed_enthalpy": 393.0,
            "requested_fan_speed": 2388.0,
            "requested_corrected_fan_speed": 100.0,
            "hpt_cooling_air_flow": 39.1,
            "lpt_cooling_air_flow": 23.1,
        }
    ]
)

graph = map_engine(sample)

query = """
PREFIX cl: <http://www.semanticweb.org/zainabalemara/ontologies/2026/9/untitled-ontology-3/>

SELECT ?cycle ?sensor ?value
WHERE {
    ?run cl:hasCycle ?cycle .
    ?cycle cl:hasReading ?reading .
    ?reading cl:measuredBy ?sensor .
    ?reading cl:sensorValue ?value .
}
"""

results = graph.query(query)

for row in results:
    print("Cycle:", row.cycle)
    print("Sensor:", row.sensor)
    print("Value:", row.value)

query2 = """
PREFIX cl: <http://www.semanticweb.org/zainabalemara/ontologies/2026/9/untitled-ontology-3/>

SELECT ?cycleNumber ?sensorCode ?value
WHERE {
    ?run cl:hasCycle ?cycle .
    ?cycle cl:cycleNumber ?cycleNumber .
    ?cycle cl:hasReading ?reading .
    ?reading cl:measuredBy ?sensor .
    ?sensor cl:sensorCode ?sensorCode .
    ?reading cl:sensorValue ?value .
}
ORDER BY ?cycleNumber
"""

results2 = graph.query(query2)

print("\nSecond SPARQL test:")

for row in results2:
    print(
        "Cycle:", row.cycleNumber,
        "Sensor:", row.sensorCode,
        "Value:", row.value
    )