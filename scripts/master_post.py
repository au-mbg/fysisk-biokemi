import os
import nbformat


def remove_exercise_block(notebook):
    indices = []
    for i, cell in enumerate(notebook.cells):
        if cell.metadata.get("exercise", False):
            indices.append(i)

    for index in reversed(indices):
        del notebook.cells[index]

    return notebook

def main(filename):
    print(f"Processing file: {filename}")
    # Add any additional processing logic here
    with open(filename, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    nb = remove_exercise_block(nb)

    with open(filename, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

if __name__ == "__main__":
    files = os.getenv("QUARTO_PROJECT_OUTPUT_FILES").split('\n')
    for file in files:
        main(file)