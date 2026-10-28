from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

if __package__:
    from .fd001_loader import get_engine, load_fd001
    from .fd001_sensors import sensors
else:
    from fd001_loader import get_engine, load_fd001
    from fd001_sensors import sensors


def correlate_engine(
    data, engine_id, reference="lpc_exit_temperature", method="pearson"
):
    # Compare measurements within one engine, without IDs or operating settings.
    if reference not in sensors or method not in ["pearson", "spearman"]:
        raise ValueError("Choose a named measurement and pearson or spearman.")
    engine = get_engine(data, engine_id)
    if len(engine) < 3:
        raise ValueError("Choose an engine with at least three recorded cycles.")
    readings = engine[list(sensors)]
    if (
        readings.isna().any().any()
        or readings.isin([float("inf"), float("-inf")]).any().any()
    ):
        raise ValueError("Correlation needs checked, finite measurements.")
    constant_readings = readings.columns[readings.nunique() <= 1].tolist()
    readings = readings.drop(columns=constant_readings)
    if reference not in readings or len(readings.columns) < 2:
        raise ValueError(
            "Choose a changing reference and at least two changing measurements."
        )

    # corr compares all pairs. corrwith compares each reading with the reference.
    matrix = readings.corr(method=method)
    if method == "spearman":
        # Spearman is Pearson on ranks. Pandas does the ranking too.
        readings = readings.rank()
    with_reference = readings.drop(columns=reference).corrwith(
        readings[reference], method="pearson"
    )
    return matrix, with_reference, constant_readings


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent.parent / "data"
    engine_id = 1
    reference = "lpc_exit_temperature"
    comparison = "hpc_exit_temperature"
    data = load_fd001(folder / "raw/train_FD001.txt")
    engine = get_engine(data, engine_id)
    output = folder / "exports"
    output.mkdir(exist_ok=True)

    # Save both correlation matrices and compare the reference scores.
    reference_scores = pd.DataFrame()
    for method in ["pearson", "spearman"]:
        matrix, with_reference, constant_readings = correlate_engine(
            data, engine_id, reference, method
        )
        matrix.to_csv(
            output / f"train_FD001_engine_{engine_id}_{method}_correlations.csv"
        )
        reference_scores[method.title()] = with_reference
    reference_scores.to_csv(
        output / f"train_FD001_engine_{engine_id}_correlations_with_{reference}.csv"
    )
    print(f"Train engine {engine_id}: correlations with {reference}")
    print(reference_scores.round(4).to_string())
    print(f"Excluded constant measurements: {', '.join(constant_readings)}")
    print("These are associations, not established causes.")

    # Pandas draws the correlation comparison and measurement scatter plot.
    labels = {}
    for reading in reference_scores.index:
        labels[reading] = sensors[reading]["name"]
    axes = reference_scores.rename(index=labels).plot.barh(
        figsize=(10, 7),
        xlim=(-1, 1),
        xlabel="Correlation coefficient",
        title=f"Train engine {engine_id}: associations with {sensors[reference]['name']}",
    )
    plt.tight_layout()
    plt.savefig(
        output / f"train_FD001_engine_{engine_id}_correlations_with_{reference}.png",
        dpi=150,
    )

    axes = engine.plot.scatter(
        x=reference,
        y=comparison,
        figsize=(7, 5),
        xlabel=f"{sensors[reference]['name']} ({sensors[reference]['unit']})",
        ylabel=f"{sensors[comparison]['name']} ({sensors[comparison]['unit']})",
        title=f"FD001 train engine {engine_id}",
    )
    plt.tight_layout()
    plt.savefig(
        output / f"train_FD001_engine_{engine_id}_{reference}_vs_{comparison}.png",
        dpi=150,
    )
    print(f"Saved correlation tables and graphs in {output}")
    plt.show()
