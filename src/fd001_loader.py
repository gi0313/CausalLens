import math
from pathlib import Path

import pandas as pd

columns = [
    "engine_id", "cycle", "setting_1", "setting_2", "setting_3",
    "sensor_1", "sensor_2", "sensor_3", "sensor_4", "sensor_5",
    "sensor_6", "sensor_7", "sensor_8", "sensor_9", "sensor_10",
    "sensor_11", "sensor_12", "sensor_13", "sensor_14", "sensor_15",
    "sensor_16", "sensor_17", "sensor_18", "sensor_19", "sensor_20", "sensor_21"
]


def load_fd001(filename, engine_id=1):
    if not Path(filename).is_file():
        raise ValueError("Data file not found.")
    try:
        data = pd.read_csv(filename, sep=r"\s+", header=None, dtype=float)
    except pd.errors.EmptyDataError:
        raise ValueError("The data file is empty.") from None
    if len(data.columns) != 26:
        raise ValueError("Each row needs 26 columns.")
    data.columns = columns

    for column in columns:
        for value in data[column]:
            if not math.isfinite(value):
                raise ValueError("The data has missing or infinite values.")
    for column in ["engine_id", "cycle"]:
        for value in data[column]:
            if value < 1 or value % 1 != 0:
                raise ValueError("Engine IDs and cycles must be positive whole numbers.")
        data[column] = data[column].astype(int)
    if data.duplicated(["engine_id", "cycle"]).any():
        raise ValueError("Duplicate engine/cycle records found.")

    data = data.sort_values(["engine_id", "cycle"])
    for number, rows in data.groupby("engine_id"):
        expected_cycle = 1
        for cycle in rows["cycle"]:
            if cycle != expected_cycle:
                raise ValueError(f"Engine {number} has missing cycles.")
            expected_cycle = expected_cycle + 1

    if type(engine_id) is not int or engine_id < 1:
        raise ValueError("Choose a positive whole engine number.")
    engine = data[data["engine_id"] == engine_id]
    if engine.empty:
        raise ValueError("Engine not found.")
    return engine.reset_index(drop=True)


if __name__ == "__main__":
    filename = Path(__file__).resolve().parent.parent / "data/raw/train_FD001.txt"
    engine_id = 1
    engine = load_fd001(filename, engine_id)
    print(f"Engine {engine_id}: {len(engine)} cycles")
    print(engine.head().to_string(index=False))
