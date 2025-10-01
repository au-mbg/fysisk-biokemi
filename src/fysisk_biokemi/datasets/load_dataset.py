import pandas as pd
from importlib.resources import files

available_datasets = {
    'chlorophyll': 'chlorophyll_adsorption.xlsx',
    'reversible_reaction': 'reversible_reaction_dataset.xlsx',
    'AA_frequency': 'AA_frequency.xlsx',
    'mCherry': 'mcherry_fpbase_spectra.csv',
    'protein_blood_plasma': 'protein_blood_plasma.xlsx',
    'dialysis_experiment': 'dialysis_experiment.xlsx',
    'adp_pyruvate': 'adp_pyruvate.csv',
    'interpret_week48': 'interpret_week48.xlsx',
    'determination_coop_week48': 'determination_coop_week48.xlsx',
    'reaction_order_week48': 'reaction_order_week48.xlsx',
    'reaction_order_activation_week48': 'reaction_order_activation_week48.csv'
}

def get_dataset_path(name: str) -> str:
    if name not in available_datasets:
        raise ValueError(f"Dataset '{name}' not found. Available datasets: {list(available_datasets.keys())}")
    return str(files('fysisk_biokemi.datasets.files').joinpath(available_datasets[name]))

def load_dataset(name: str):
    if name not in available_datasets:
        raise ValueError(f"Dataset '{name}' not found. Available datasets: {list(available_datasets.keys())}")

    dataset_path = get_dataset_path(name)

    if dataset_path.endswith('.csv'):
        df = pd.read_csv(dataset_path)
    elif dataset_path.endswith('.xlsx'):    
        df = pd.read_excel(dataset_path)

    return df

if __name__ == "__main__":

    data = load_dataset('chlorophyll')
    print(data)