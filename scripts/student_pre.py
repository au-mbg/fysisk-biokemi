import os

if __name__ == "__main__":
    files = os.getenv("QUARTO_PROJECT_INPUT_FILES").split('\n')
    for file in files:
        print(f"Processing file: {file}")
