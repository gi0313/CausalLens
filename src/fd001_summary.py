from pathlib import Path

import pandas as pd


def summarize_data(data):
    # Count cycles for each engine in the loaded data.
    cycles = data.groupby("engine_id")["cycle"].agg(["min", "max", "count"])

    # Return the results so a page or another script can use them.
    summary = {
        "records": len(data),
        "engines": len(cycles),
        "shortest_history": cycles["count"].min(),
        "longest_history": cycles["count"].max(),
        "average_history": cycles["count"].mean(),
        "first_cycle": data["cycle"].min(),
        "last_cycle": data["cycle"].max(),
        "missing_values": data.isna().sum().sum(),
        "duplicate_rows": data.duplicated().sum(),
        "duplicate_engine_cycles": data.duplicated(["engine_id", "cycle"]).sum(),
        "cycles_per_engine": cycles,
        "statistics": data.iloc[:, 2:].agg(["min", "max", "mean"]).T,
    }
    return summary


# Print the examples only when this file is started directly.
if __name__ == "__main__":
    from fd001_loader import load_fd001

    folder = Path(__file__).resolve().parent.parent / "data" #Change filepath
    test_engine_count = 0

    # Explain the operating settings before showing their statistics.
    print("setting_1: altitude (height above sea level).")
    print("setting_2: Mach number (speed / speed of sound; no unit).")
    print("setting_3: throttle resolver angle (requested engine power).")
    print("FD001 uses one operating condition, with setting_3 fixed at 100.")
    print("Settings 1 and 2 stay close to zero. Original values are kept.")
    print("Confirm the stored altitude and throttle scales before converting units.")

    # Load and summarize the training and test files separately.
    for name in ["train", "test"]:
        data = load_fd001(folder / f"{name}_FD001.txt")
        summary = summarize_data(data)
        if name == "test":
            test_engine_count = summary["engines"]

        print(f"\n{name.upper()} FD001")
        print(f"Records: {summary['records']} | Engines: {summary['engines']}")
        print(f"Shortest history: {summary['shortest_history']} cycles")
        print(f"Longest history: {summary['longest_history']} cycles")
        print(f"Average history: {summary['average_history']:.2f} cycles")
        print(f"First recorded cycle: {summary['first_cycle']}")
        print(f"Last recorded cycle: {summary['last_cycle']}")
        print(f"Missing values: {summary['missing_values']}")
        print(f"Duplicate rows: {summary['duplicate_rows']}")
        print(f"Duplicate engine/cycle records: {summary['duplicate_engine_cycles']}")
        print("Settings and sensor statistics:")
        # Show small averages without rounding them to zero.
        print(summary["statistics"].round(8).to_string())

    # RUL gives one remaining-life answer for each test engine.
    rul = pd.read_csv(folder / "RUL_FD001.txt", sep=r"\s+", header=None)
    if len(rul.columns) != 1:
        raise ValueError("Expected one RUL column.")
    rul.columns = ["remaining_cycles"]
    if len(rul) != test_engine_count:
        raise ValueError("RUL answers must match the number of test engines.")
    print("\nRUL FD001")
    print(f"Answers: {len(rul)}")
    print(f"Missing values: {rul.isna().sum().sum()}")
    print(rul.agg(["min", "max", "mean"]).round(2).to_string())
    print("RUL tells us how many cycles each test engine has left after its final recorded row.")
