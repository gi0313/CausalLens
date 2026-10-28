# Shared names, components, and units for the FD001 readings.
# Keep this dictionary in the raw file's measurement order.
# Source: NASA's Damage Propagation Modeling paper, Table 2.
sensors = {
    "fan_inlet_temperature": {
        "symbol": "T2",
        "name": "Fan-inlet temperature",
        "component": "Fan",
        "unit": "°R",
    },
    "lpc_exit_temperature": {
        "symbol": "T24",
        "name": "LPC-exit temperature",
        "component": "LPC",
        "unit": "°R",
    },
    "hpc_exit_temperature": {
        "symbol": "T30",
        "name": "HPC-exit temperature",
        "component": "HPC",
        "unit": "°R",
    },
    "lpt_exit_temperature": {
        "symbol": "T50",
        "name": "LPT-exit temperature",
        "component": "LPT",
        "unit": "°R",
    },
    "fan_inlet_pressure": {
        "symbol": "P2",
        "name": "Fan-inlet pressure",
        "component": "Fan",
        "unit": "psia",
    },
    "bypass_duct_pressure": {
        "symbol": "P15",
        "name": "Bypass-duct pressure",
        "component": "Fan bypass",
        "unit": "psia",
    },
    "hpc_exit_total_pressure": {
        "symbol": "P30",
        "name": "HPC-exit total pressure",
        "component": "HPC",
        "unit": "psia",
    },
    "fan_speed": {
        "symbol": "Nf",
        "name": "Fan speed",
        "component": "Low-pressure shaft (N1)",
        "unit": "rpm",
    },
    "core_speed": {
        "symbol": "Nc",
        "name": "Core speed",
        "component": "High-pressure shaft (N2)",
        "unit": "rpm",
    },
    "engine_pressure_ratio": {
        "symbol": "epr",
        "name": "Pressure ratio P50/P2",
        "component": "Fan inlet / LPT exit",
        "unit": "unitless",
    },
    "hpc_exit_static_pressure": {
        "symbol": "Ps30",
        "name": "HPC-exit static pressure",
        "component": "HPC",
        "unit": "psia",
    },
    "fuel_flow_per_hpc_static_pressure": {
        "symbol": "phi",
        "name": "Fuel flow / HPC static pressure",
        "component": "Fuel system / HPC",
        "unit": "pps/psi",
    },
    "corrected_fan_speed": {
        "symbol": "NRf",
        "name": "Corrected fan speed",
        "component": "Low-pressure shaft (N1)",
        "unit": "rpm",
    },
    "corrected_core_speed": {
        "symbol": "NRc",
        "name": "Corrected core speed",
        "component": "High-pressure shaft (N2)",
        "unit": "rpm",
    },
    "bypass_ratio": {
        "symbol": "BPR",
        "name": "Bypass-to-core airflow ratio",
        "component": "Bypass / core",
        "unit": "unitless",
    },
    "burner_fuel_air_ratio": {
        "symbol": "farB",
        "name": "Burner fuel-to-air ratio",
        "component": "Combustor",
        "unit": "unitless",
    },
    "bleed_enthalpy": {
        "symbol": "htBleed",
        "name": "Bleed enthalpy",
        "component": "Bleed-air system",
        "unit": "not specified",
    },
    "requested_fan_speed": {
        "symbol": "Nf_dmd",
        "name": "Requested fan speed",
        "component": "Fan controller (N1)",
        "unit": "rpm",
    },
    "requested_corrected_fan_speed": {
        "symbol": "PCNfR_dmd",
        "name": "Requested corrected fan speed",
        "component": "Fan controller (N1)",
        "unit": "unconfirmed scale",
    },
    "hpt_cooling_air_flow": {
        "symbol": "W31",
        "name": "HPT cooling-air flow",
        "component": "HPT",
        "unit": "lbm/s",
    },
    "lpt_cooling_air_flow": {
        "symbol": "W32",
        "name": "LPT cooling-air flow",
        "component": "LPT",
        "unit": "lbm/s",
    },
}

# Requested corrected fan speed is stored as 100. Confirm its scale before using rpm.
# Bleed enthalpy units and the exact extraction location are not specified.
