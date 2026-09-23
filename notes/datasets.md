# Managing datasets

Course datasets are stored in
`course-utils/src/fysisk_biokemi/datasets/files/`. Their metadata and the names
accepted by the Python API are defined in
`course-utils/src/fysisk_biokemi/datasets/metadata.yml`.

The metadata file is the source of truth for both the `load_dataset()` API and
the datasets page on the Quarto site. Do not add dataset mappings directly to
`load_dataset.py`.

## Add a dataset

Adding a dataset has two steps:

1. Add the data file to `course-utils/src/fysisk_biokemi/datasets/files/`.
2. Add an entry keyed by the exact filename under `datasets` in `metadata.yml`.

Each metadata entry has these fields:

- `shortnames`: A non-empty list of unique names accepted by `load_dataset()`.
- `week`: The course week shown on the datasets page, or `null` when unassigned.
- `exercise`: The related exercise filename, or `null` when unassigned.
- `original_name`: The source file's original name.
- `description`: A short description shown on the datasets page.

For example:

```yaml
datasets:
  example-data.csv:
    shortnames: ["example_data"]
    week: 45
    exercise: "example-exercise.qmd"
    original_name: "example-data.csv"
    description: "Example measurements"
```

Only values explicitly listed in `shortnames` can be passed to
`load_dataset()`; filenames are not accepted automatically. If a dataset or
exercise is renamed, retain its existing shortnames so old notebooks continue
to work. Multiple aliases can point to the same file:

```yaml
shortnames: ["old_name", "preferred_name"]
```

The loader supports CSV (`.csv`), Excel (`.xlsx`), and plain text (`.txt`)
files. CSV and Excel files load as pandas data frames; text files load as
strings.

## Verify changes

From the repository root, run:

```bash
pixi run render master
```
The render checks the datasets page still uses the same metadata successfully.
