from importlib.resources import files

import pandas as pd
import yaml


def _load_available_datasets() -> dict[str, str]:
    metadata_path = files("fysisk_biokemi.datasets").joinpath("metadata.yml")
    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        datasets = yaml.safe_load(metadata_file)["datasets"]

    return {
        shortname: filename
        for filename, metadata in datasets.items()
        for shortname in metadata["shortnames"]
    }


available_datasets = _load_available_datasets()


def get_dataset_path(name: str) -> str:
    if name not in available_datasets:
        raise ValueError(
            f"Dataset '{name}' not found. "
            f"Available datasets: {list(available_datasets.keys())}"
        )
    return str(
        files("fysisk_biokemi.datasets.files").joinpath(available_datasets[name])
    )


def load_dataset(name: str):
    if name not in available_datasets:
        raise ValueError(
            f"Dataset '{name}' not found. "
            f"Available datasets: {list(available_datasets.keys())}"
        )

    dataset_path = get_dataset_path(name)

    if dataset_path.endswith(".csv"):
        data = pd.read_csv(dataset_path)
    elif dataset_path.endswith(".xlsx"):
        data = pd.read_excel(dataset_path)
    elif dataset_path.endswith(".txt"):
        with open(dataset_path, "r", encoding="utf-8") as file:
            data = file.read().strip()

    return data


if __name__ == "__main__":
    for dataset_name in available_datasets.keys():
        print(f"Loading dataset: {dataset_name}")
        try:
            data = load_dataset(dataset_name)
        except Exception:
            print(f"Failed to load dataset: {dataset_name}")
            continue
