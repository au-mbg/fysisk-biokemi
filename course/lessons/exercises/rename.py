from shutil import move
from pathlib import Path


files = Path.cwd().glob('*.qmd')

for file in files:

    name_bits = file.stem.split('_')
    new_name = '_'.join(name_bits[1:]) + '.qmd'
    print(file.stem, new_name)

    move(file, file.parent / new_name)
