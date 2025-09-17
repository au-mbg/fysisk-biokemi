from importlib.resources import files
from jupyterquiz import display_quiz
import json

def get_quiz(index: int = 1):
    path = files("fysisk_biokemi.quiz").joinpath(f"questions/quiz_{index}.json")
    data = json.load(path.open())
    display_quiz([data])

if __name__ == "__main__":

    get_quiz(1)
