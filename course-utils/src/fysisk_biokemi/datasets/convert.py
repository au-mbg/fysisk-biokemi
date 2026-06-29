# Convert all datasets to excel

import pandas as pd

def convert_datasets_to_excel():
    datasets = {
        'chlorophyll': 'chlorophyll_adsorption.txt',
        'reversible_reaction': 'reversible_reaction_dataset.csv',
    }

    for name, file in datasets.items():
        if file.endswith('.txt'):
            df = pd.read_csv(file, sep='\s+', comment='#')
        elif file.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            raise ValueError(f"Unsupported file format for {file}")

        excel_file = f"{name}.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"Converted {file} to {excel_file}")

if __name__ == "__main__":
    convert_datasets_to_excel()