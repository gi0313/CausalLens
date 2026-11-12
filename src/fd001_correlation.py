from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

if __package__:
    from .fd001_loader import get_engine, load_fd001
    from .fd001_sensors import sensors
else:
    from fd001_loader import get_engine, load_fd001
    from fd001_sensors import sensors


def correlate_engine(data, engine_id):
    # Use all recorded cycles for one engine and only the 24 measured variables.
    engine = get_engine(data, engine_id)
    if len(engine) < 3:
        raise ValueError("Choose an engine with at least three recorded cycles.")
    columns = ["altitude", "mach_number", "throttle_resolver_angle"] + list(sensors)
    readings = engine[columns]
    if (
        readings.isna().any().any()
        or readings.isin([float("inf"), float("-inf")]).any().any()
    ):
        raise ValueError("Correlation needs checked, finite measurements and settings.")

    # Keep constants. Pandas returns NaN because their correlation is undefined.
    return readings.corr(method="pearson")


def plot_correlation(matrix, title="Pearson correlation matrix"):
    # Use the shared measurement names on both axes.
    names = {
        "altitude": "Altitude",
        "mach_number": "Mach number",
        "throttle_resolver_angle": "Throttle resolver angle",
    }
    for reading in sensors:
        names[reading] = sensors[reading]["name"]
    labels = []
    for column in matrix.columns:
        labels.append(names[column])

    # Gray means undefined. White means a correlation near zero.
    colors = plt.get_cmap("coolwarm").copy()
    colors.set_bad("gray")
    figure, axes = plt.subplots(figsize=(15, 13))
    image = axes.matshow(matrix, cmap=colors, vmin=-1, vmax=1)
    axes.set_xticks(range(len(labels)), labels, rotation=90, fontsize=9)
    axes.set_yticks(range(len(labels)), labels, fontsize=9)
    axes.xaxis.tick_bottom()
    figure.colorbar(image, ax=axes, shrink=0.8, label="Pearson correlation")
    axes.set_title(title, pad=15)
    figure.legend(
        handles=[Patch(facecolor="gray", label="Undefined (constant variable)")],
        loc="lower left", bbox_to_anchor=(0.23, 0.005), frameon=False,
    )
    figure.tight_layout(rect=(0, 0.03, 1, 1))
    return figure


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent.parent / "data"
    engine_id = 1
    data = load_fd001(folder / "raw/train_FD001.txt")
    engine = get_engine(data, engine_id)
    matrix = correlate_engine(data, engine_id)
    print(f"FD001 train engine {engine_id}: all {len(engine)} recorded cycles")
    print(matrix.round(3).to_string())
    print("NaN / gray means undefined for a constant variable, not zero.")
    print("Correlation does not establish causation.")

    # Display the matrix. The returned figure can also be saved by its caller.
    figure = plot_correlation(
        matrix,
        title=f"FD001 train engine {engine_id}: Pearson correlation ({len(engine)} cycles)",
    )
    plt.show()
