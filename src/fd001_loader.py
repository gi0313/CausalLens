from numbers import Integral
from pathlib import Path

import pandas as pd

# Support the Run button and imports from the project folder.
if __package__:
    from .fd001_sensors import sensors
else:
    from fd001_sensors import sensors

# Name the columns in raw file order, using the actual quantities.
# Keep altitude and throttle values unchanged until their scales are confirmed.
columns = [
    "engine_id",
    "cycle",
    "altitude",
    "mach_number",
    "throttle_resolver_angle",
] + list(sensors)


def load_fd001(filename, split=None):
    # Standard filenames tell us which split this engine belongs to.
    if split is None:
        if Path(filename).name == "train_FD001.txt":
            split = "train"
        elif Path(filename).name == "test_FD001.txt":
            split = "test"
    if split not in ["train", "test"]:
        raise ValueError("Pass split='train' or split='test' for a renamed file.")

    # Check that the file exists and has the expected columns.
    if not Path(filename).is_file():
        raise ValueError("Data file not found.")
    try:
        data = pd.read_csv(filename, sep=r"\s+", header=None, dtype=float)
    except pd.errors.EmptyDataError:
        raise ValueError("The data file is empty.") from None
    if len(data.columns) != 26:
        raise ValueError("Each row needs 26 columns.")
    data.columns = columns

    # Pandas identifies the columns with missing values.
    missing = data.isna().sum()
    if missing.any():
        raise ValueError(f"Missing values:\n{missing[missing > 0].to_string()}")
    if data.isin([float("inf"), float("-inf")]).any().any():
        raise ValueError("The data has infinite values.")
    # Engine IDs and cycles must be positive whole numbers.
    for column in ["engine_id", "cycle"]:
        if (data[column] < 1).any() or (data[column] % 1 != 0).any():
            raise ValueError("Engine IDs and cycles must be positive whole numbers.")
        data[column] = data[column].astype(int)
    # Each engine should have only one record for each cycle.
    duplicates = data[data.duplicated(["engine_id", "cycle"], keep=False)]
    if not duplicates.empty:
        counts = (
            duplicates.groupby(["engine_id", "cycle"])
            .size()
            .reset_index(name="records")
        )
        raise ValueError(
            f"Duplicate engine/cycle records:\n{counts.to_string(index=False)}"
        )

    # Put cycles in order and check for missing cycle numbers.
    data = data.sort_values(["engine_id", "cycle"])
    for number, rows in data.groupby("engine_id"):
        if rows["cycle"].iloc[0] != 1 or (rows["cycle"].diff().dropna() != 1).any():
            raise ValueError(f"Engine {number} has missing cycles.")

    # Keep the 26 numeric columns first. IDs and cycles are whole numbers.
    # Add dataset, split, and cycle_id as text after those columns.
    data["dataset"] = "FD001"
    data["split"] = split
    data["cycle_id"] = (
        f"FD001/{split}/engine/"
        + data["engine_id"].astype(str)
        + "/cycle/"
        + data["cycle"].astype(str)
    )
    return data.reset_index(drop=True)


def get_engine(data, engine_id):
    # Select one engine from the data that was already loaded.
    if (
        isinstance(engine_id, bool)
        or not isinstance(engine_id, Integral)
        or engine_id < 1
    ):
        raise ValueError("Choose a positive whole engine number.")
    if data["split"].nunique() != 1:
        raise ValueError("Select one train or test split before selecting an engine.")
    engine = data[data["engine_id"] == engine_id]
    if engine.empty:
        raise ValueError("Engine not found.")
    return engine.sort_values("cycle").reset_index(drop=True)


def get_observations(data):
    # Melt changes the wide table into one row per measurement.
    observations = data.melt(
        id_vars=["dataset", "split", "engine_id", "cycle", "cycle_id"],
        value_vars=list(sensors),
        var_name="measurement",
        value_name="value",
    )
    # Join the shared names, components, and units onto each reading.
    definitions = pd.DataFrame.from_dict(sensors, orient="index")
    definitions.index.name = "measurement"
    observations = observations.merge(
        definitions.reset_index(), on="measurement", validate="many_to_one"
    )
    observations["observation_id"] = (
        observations["cycle_id"] + "/" + observations["measurement"]
    )
    observations = observations.sort_values(
        ["split", "engine_id", "cycle", "measurement"]
    )
    return observations[
        [
            "observation_id",
            "dataset",
            "split",
            "engine_id",
            "cycle",
            "measurement",
            "name",
            "symbol",
            "component",
            "unit",
            "value",
        ]
    ].reset_index(drop=True)


def load_rul(filename, test_data):
    # RUL line 1 belongs to test engine 1 at its last recorded cycle.
    if test_data.empty or not (test_data["split"] == "test").all():
        raise ValueError("Load the test split before loading its RUL answers.")
    engine_ids = sorted(test_data["engine_id"].unique())
    for number, engine_id in enumerate(engine_ids, start=1):
        if engine_id != number:
            raise ValueError("FD001 test engine IDs must run from 1 without gaps.")
    if not Path(filename).is_file():
        raise ValueError("RUL file not found.")
    try:
        rul = pd.read_csv(filename, sep=r"\s+", header=None, dtype=float)
    except pd.errors.EmptyDataError:
        raise ValueError("The RUL file is empty.") from None
    if len(rul.columns) != 1 or len(rul) != len(engine_ids):
        raise ValueError("Expected one RUL answer for every test engine.")
    rul.columns = ["remaining_cycles"]
    remaining = rul["remaining_cycles"]
    if (
        remaining.isna().any()
        or remaining.isin([float("inf"), float("-inf")]).any()
        or (remaining < 0).any()
        or (remaining % 1 != 0).any()
    ):
        raise ValueError("RUL answers must be non-negative whole numbers.")
    rul["remaining_cycles"] = rul["remaining_cycles"].astype(int)

    # Match each answer to its engine and final recorded cycle.
    rul["dataset"] = "FD001"
    rul["split"] = "test"
    rul["engine_id"] = engine_ids
    rul["last_cycle"] = test_data.groupby("engine_id")["cycle"].max().to_numpy()
    return rul[["dataset", "split", "engine_id", "last_cycle", "remaining_cycles"]]


# Loads engine 1 when you press Run.
if __name__ == "__main__":
    folder = Path(__file__).resolve().parent.parent / "data"
    engine_id = 100
    data = load_fd001(folder / "raw/train_FD001.txt")
    engine = get_engine(data, engine_id)

    # Show a short summary and the first five readings.
    print(f"Loaded {len(data)} records from {data['engine_id'].nunique()} engines.")
    print("Data checks passed.")
    print(f"Engine {engine_id}: {len(engine)} cycles.")
    print(engine[["engine_id", "cycle", "lpc_exit_temperature"]].head())
    observations = get_observations(engine)
    example = observations[observations["measurement"] == "lpc_exit_temperature"].iloc[
        0
    ]
    print(f"LPC-exit temperature ID: {example['observation_id']}")

    # Save the selected engine for sharing.
    output = folder / "exports"
    output.mkdir(exist_ok=True)
    engine.to_csv(output / f"train_FD001_engine_{engine_id}.csv", index=False)
    print(f"Saved data/exports/train_FD001_engine_{engine_id}.csv")
    observations.to_csv(
        output / f"train_FD001_engine_{engine_id}_observations.csv", index=False
    )
    print(f"Saved data/exports/train_FD001_engine_{engine_id}_observations.csv")
