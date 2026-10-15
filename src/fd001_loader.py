import math
from numbers import Integral
from pathlib import Path

import pandas as pd

# Name the columns in the same order as the data file.
columns = ["engine_id", "cycle", "setting_1", "setting_2", "setting_3"]
for number in range(1, 22):
    columns.append(f"sensor_{number}")


def load_fd001(filename):
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

    # Reject missing values and infinity.
    for column in columns:
        for value in data[column]:
            if not math.isfinite(value):
                raise ValueError("The data has missing or infinite values.")
    # Engine IDs and cycles must be positive whole numbers.
    for column in ["engine_id", "cycle"]:
        for value in data[column]:
            if value < 1 or value % 1 != 0:
                raise ValueError(
                    "Engine IDs and cycles must be positive whole numbers."
                )
        data[column] = data[column].astype(int)
    # Each engine should have only one record for each cycle.
    if data.duplicated(["engine_id", "cycle"]).any():
        raise ValueError("Duplicate engine/cycle records found.")

    # Put cycles in order and check for missing cycle numbers.
    data = data.sort_values(["engine_id", "cycle"])
    for number, rows in data.groupby("engine_id"):
        expected_cycle = 1
        for cycle in rows["cycle"]:
            if cycle != expected_cycle:
                raise ValueError(f"Engine {number} has missing cycles.")
            expected_cycle = expected_cycle + 1

    return data.reset_index(drop=True)


def get_engine(data, engine_id):
    # Select one engine from the data that was already loaded.
    if isinstance(engine_id, bool) or not isinstance(engine_id, Integral) or engine_id < 1:
        raise ValueError("Choose a positive whole engine number.")
    engine = data[data["engine_id"] == engine_id]
    if engine.empty:
        raise ValueError("Engine not found.")
    return engine.sort_values("cycle").reset_index(drop=True)


# Loads engine 1 when you press Run.
if __name__ == "__main__":
    folder = Path(__file__).resolve().parent.parent / "data"
    engine_id = 1
    data = load_fd001(folder / "raw/train_FD001.txt")
    engine = get_engine(data, engine_id)

    # Show a short summary and the first five readings.
    print(f"Loaded {len(data)} records from {data['engine_id'].nunique()} engines.")
    print("Data checks passed.")
    print(f"Engine {engine_id}: {len(engine)} cycles.")
    print(engine[["engine_id", "cycle", "sensor_2"]].head())

    # Save the selected engine for sharing.
    output = folder / "exports"
    output.mkdir(exist_ok=True)
    engine.to_csv(output / f"train_FD001_engine_{engine_id}.csv", index=False)
    print(f"Saved data/exports/train_FD001_engine_{engine_id}.csv")
