from pathlib import Path

# Support the Run button and imports from the project folder.
if __package__:
    from .fd001_loader import columns, load_fd001, load_rul
else:
    from fd001_loader import columns, load_fd001, load_rul


def summarize_data(data):
    if data["split"].nunique() != 1:
        raise ValueError("Summarize one train or test split at a time.")
    # Count cycles for each engine in the loaded data.
    cycles = data.groupby("engine_id")["cycle"].agg(["min", "max", "count"])
    # Keep every row involved in a repeated engine-cycle pair.
    duplicate_records = data.loc[data.duplicated(["engine_id", "cycle"], keep=False), columns]
    duplicate_counts = duplicate_records.groupby(["engine_id", "cycle"]).size().reset_index(name="records")

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
        "duplicate_rows": data.duplicated(subset=columns).sum(),
        "duplicate_engine_cycles": data.duplicated(["engine_id", "cycle"]).sum(),
        "duplicate_records": duplicate_records,
        "duplicate_counts": duplicate_counts,
        "cycles_per_engine": cycles,
        "history_statistics": cycles["count"].describe(),
        # Identity columns are labels, so only summarize settings and readings.
        "statistics": data[columns[2:]].describe().T,
    }
    return summary


# Print the examples only when this file is started directly.
if __name__ == "__main__":
    folder = Path(__file__).resolve().parent.parent / "data/raw"

    output = folder.parent / "exports"
    output.mkdir(exist_ok=True)

    # Load and summarize the training and test files separately.
    for name in ["train", "test"]:
        data = load_fd001(folder / f"{name}_FD001.txt")
        summary = summarize_data(data)
        print(f"\n{name.upper()} FD001")
        print(f"Records: {summary['records']} | Engines: {summary['engines']}")
        print(f"Missing values: {summary['missing_values']}")
        print(f"Extra duplicate rows: {summary['duplicate_rows']}")
        print(f"Extra duplicate engine-cycle records: {summary['duplicate_engine_cycles']}")
        if not summary["duplicate_records"].empty:
            print(summary["duplicate_counts"].to_string(index=False))
            print(summary["duplicate_records"].to_string(index=False))
        print("Cycles per engine: describe()")
        print(summary["history_statistics"].round(2).to_string())
        print("Operating conditions and measurements: describe()")
        # Keep small values visible and avoid displaying negative zero.
        display = summary["statistics"].round(8).replace(-0.0, 0.0)
        print(display.to_string(float_format="{:.8g}".format))
        summary["statistics"].to_csv(output / f"{name}_FD001_statistics.csv")
        summary["duplicate_records"].to_csv(output / f"{name}_FD001_duplicate_records.csv", index=False)
        summary["duplicate_counts"].to_csv(output / f"{name}_FD001_duplicate_counts.csv", index=False)

    # RUL gives one remaining-life answer for each test engine.
    # The loop ends with test data. Reuse it to match the RUL answers.
    rul = load_rul(folder / "RUL_FD001.txt", data)
    print("\nRUL FD001")
    print(f"Answers: {len(rul)}")
    print(f"Missing values: {rul.isna().sum().sum()}")
    print(rul[["remaining_cycles"]].describe().round(2).to_string())
    rul[["remaining_cycles"]].describe().to_csv(output / "RUL_FD001_statistics.csv")
