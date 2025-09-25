import pandas as pd
from importlib.resources import files

available_datasets = {
    'chlorophyll': 'chlorophyll_adsorption.xlsx',
    'reversible_reaction': 'reversible_reaction_dataset.xlsx',
    'AA_frequency': 'AA_frequency.xlsx',
}

def get_dataset_path(name: str) -> str:
    if name not in available_datasets:
        raise ValueError(f"Dataset '{name}' not found. Available datasets: {list(available_datasets.keys())}")
    return str(files('fysisk_biokemi.datasets.files').joinpath(available_datasets[name]))

def load_dataset(name: str):
    if name not in available_datasets:
        raise ValueError(f"Dataset '{name}' not found. Available datasets: {list(available_datasets.keys())}")

    dataset_path = get_dataset_path(name)

    df = pd.read_excel(dataset_path)
    return df

if __name__ == "__main__":

    data = load_dataset('chlorophyll')
    print(data)