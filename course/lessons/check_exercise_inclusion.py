from pathlib import Path
import re

def read_week_file(file_path):
    # Extract lines that have {{< include exercises/NAME.qmd >}}
    exercises_included = []
    with open(file_path, 'r') as file:
        for line in file:
            
            if '{{< include exercises/' in line or '{{< include intros/' in line:
                parts = line.split(' ')
                file_path = parts[2]
                exercises_included.append(file_path)
    return exercises_included


if __name__ == "__main__":

    included_exercises = {}
    for week_number in [45, 46, 47, 48]:
        data = read_week_file(Path(f'week_{week_number}.qmd'))
        included_exercises[week_number] = data

    # All exercises
    all_exercises = [f"exercises/{f.name}" for f in Path('exercises').glob('*.qmd')]
    all_exercises += [f"intros/{f.name}" for f in Path('intros').glob('*.qmd')]

    # Check which exercises are not included
    included_set = set()
    for week, exercises in included_exercises.items():
        included_set.update(exercises)
    all_set = set(all_exercises)

    not_included = all_set - included_set
    print("Exercises not included in any week:")
    for exercise in not_included:
        print(f" - {exercise}")

    # Check if exercises are included in multiple weeks
    exercise_count = {}
    for week, exercises in included_exercises.items():
        for exercise in exercises:
            if exercise not in exercise_count:
                exercise_count[exercise] = []
            exercise_count[exercise].append(week)
    print("\nExercises included in multiple weeks:")
    for exercise, weeks in exercise_count.items():
        if len(weeks) > 1:
            print(f" - {exercise} included in weeks: {weeks}")

    # Check that no exercises are included that don't exist
    print("\nExercises included that do not exist:")
    for exercise in included_set:
        if exercise not in all_set:
            print(f" - {exercise} does not exist")

    # How many exercise per week: 
    print("\nNumber of exercises per week:")
    for week, exercises in included_exercises.items():
        print(f" - Week {week}: {len(exercises)} exercises")
        for exercise in exercises:
            print(f"    - {exercise}")