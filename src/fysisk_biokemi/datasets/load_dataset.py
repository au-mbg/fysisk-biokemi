import pandas as pd
from importlib.resources import files

available_datasets = {
    'chlorophyll': 'chlorophyll_adsorption.xlsx',
    'reversible_reaction': 'reversible_reaction_dataset.xlsx',
    # Week 46:
    'AA_frequency': 'week46_1_AA_frequency.xlsx',
    # Week 47:
    'mCherry': 'week47_2_mcherry_fpbase_spectra.csv',
    'protein_blood_plasma': 'week47_3_protein_blood_plasma.xlsx',
    'dialysis_experiment': 'week47_7_dialysis_experiment.xlsx',
    'adp_pyruvate': 'week47_8_adp_pyruvate.csv',

    # Week 48:
    'interpret_week48': 'week48_1_interpret.xlsx',
    'determination_coop_week48': 'week48_2_determination_coop.xlsx',
    'reaction_order_week48': 'week48_4_reaction_order.xlsx',
    'reaction_order_activation_week48': 'week48_7_reaction_order_activation.csv',

    # Week 49:
    'week49_1': 'week49_1.xlsx',
    'week49_2': 'week49_2.xlsx',
    'week49_6': 'week49_6_inhib.xlsx',
    'week49_7': 'week49_7_inhib_II.xlsx',

    # Other
    'titin': 'titin.txt',
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
        data = pd.read_csv(dataset_path)
    elif dataset_path.endswith('.xlsx'):    
        data = pd.read_excel(dataset_path)
    elif dataset_path.endswith('.txt'):
        with open(dataset_path, 'r') as file:
            data = file.read().strip()

    return data

if __name__ == "__main__":

    for dataset_name in available_datasets.keys():
        print(f"Loading dataset: {dataset_name}")
        try:
            data = load_dataset(dataset_name)
        except: 
            print(f"Failed to load dataset: {dataset_name}")
            continue
