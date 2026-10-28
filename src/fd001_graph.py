from pathlib import Path

import matplotlib.pyplot as plt

# Support the Run button and imports from the project folder.
if __package__:
    from .fd001_loader import get_engine, load_fd001
    from .fd001_sensors import sensors
else:
    from fd001_loader import get_engine, load_fd001
    from fd001_sensors import sensors


def plot_sensor(data, engine_id, reading):
    # Pandas creates the line graph using the actual measurement name.
    if reading not in sensors:
        raise ValueError("Choose a measurement from fd001_sensors.py.")
    engine = get_engine(data, engine_id)
    info = sensors[reading]
    split = engine.iloc[0]["split"]

    # Use the shared names and units to label the graph.
    axes = engine.plot(
        x="cycle", y=reading, figsize=(9, 4.5), legend=False,
        title=f"FD001 {split} engine {engine_id}: {info['name']}",
        xlabel="Operating cycle", ylabel=f"{info['name']} ({info['unit']})",
    )
    figure = axes.figure
    figure.tight_layout()
    return figure


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent.parent / "data"
    engine_id = 1
    reading = "lpc_exit_temperature"
    data = load_fd001(folder / "raw/train_FD001.txt")
    figure = plot_sensor(data, engine_id, reading)

    # Save the same graph that opens when you press Run.
    output = folder / "exports"
    output.mkdir(exist_ok=True)
    filename = output / f"train_FD001_engine_{engine_id}_{reading}.png"
    figure.savefig(filename, dpi=150)
    print(f"Saved {filename}")
    plt.show()
