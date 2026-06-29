import pandas as pd
from importlib.resources import files

available_datasets = {    
    'chlorophyll': 'chlorophyll_adsorption.xlsx',
    'reversible_reaction': 'reverse_reaction.xlsx',
    'diff_q_keq': 'diff_q_keq_data.xlsx',
    'deter_delta_h': 'deter_delta_h_data.xlsx',
    'binding_data_sq': 'binding_data_sq.xlsx',
    'kinetics_LØ': 'kinetics_data.xlsx',
    'exp_decay_data': 'exp_decay_data.xlsx',
    # Week 45:
    'apo_holo': 'uv-spec-apo-holo-myo.csv',
    'AA_frequency': 'averag-prope-amino-acids.xlsx',
    # Week 46:
    'dialysis_experiment': 'dialys-exper.xlsx',
    'adp_pyruvate': 'adp-bindin-pyruva-kinase.csv',
    'interpret_week48': 'inter-bindin-data.xlsx',
    'determination_coop_week48': 'deter-type-streng-coope.xlsx',
    # Week 47:
    'reaction_order_week48': 'reaction-orders.xlsx',
    'reaction_order_activation_week48': 'deter-reacti-order-activ.csv',
    'week49_1': 'design-enzyme-kineti-exper.xlsx',
    'week49_2': 'analys-data-set-obeyin.xlsx',
    # Week 48:
    'week49_6': 'enzyme-inhib-i.xlsx',
    'week49_7': 'enzyme-inhib-ii.xlsx',
    'atcase': 'enzyme-behav-atcase.csv',

    'week47_1_emi': 'trypt-absor-fluor-emission.xlsx',
    'week47_1_ext': 'trypt-absor-fluor-extinction.xlsx',
    'week47_1_ph2': 'trypt-absor-fluor-ph2.xlsx',
    'week47_1_ph7': 'trypt-absor-fluor-ph7.xlsx',

    'titin': 'extin-coeff-human-myogl.txt',
    'mCherry': 'the-fluor-protei-mcherr.csv',
    'protein_blood_plasma': 'protei-blood-plasma.xlsx',
    
    # New exercise-based names (preferred):
    'design-enzyme-kineti-exper.xlsx': 'design-enzyme-kineti-exper.xlsx',
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
