import pandas as pd
from importlib.resources import files

available_datasets = {
    'chlorophyll': 'chlorophyll_adsorption.txt',
    'reversible_reaction': 'reversible_reaction_dataset.csv',
}

def load_dataset(name: str):
    if name not in available_datasets:
        raise ValueError(f"Dataset '{name}' not found. Available datasets: {list(available_datasets.keys())}")

    dataset_path = files('fysisk_biokemi.datasets').joinpath(available_datasets[name])

    df = pd.read_csv(dataset_path, sep='\s+', comment='#')
    return df

if __name__ == "__main__":

    data = load_dataset('reversible_reaction')
    print(data)