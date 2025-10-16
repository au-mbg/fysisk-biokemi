# Fysisk biokemi & dataanalyse

## Files and folders
- `course/`: Contains all the files for the exercises and for making the different document types. 
- `source/`: Contains a small Python package, mainly used for the widgets and the datasets. 
- `pyproject.toml`: Dependencies of the Python package (and therefore also controls dependencies for the exercises.)
- `.github/workflows/`: Github workflow for making and hosting the static website.

## Python environment


### Using `uv`

To work with or on the exercises or Python files locally a virtual environment (venv) is 
recommended. The nicest way is by using `uv` which can be installed from [here](https://docs.astral.sh/uv/)
With `uv` installed a venv that includes all the dependencies can be created like so
```bash
uv sync
```
The environment will be named `.venv` and needs to be activated with `source .venv/bin/activate`.

### No `uv`

To make a virtual environment without `uv` run this command from the root
```
python3 -m venv .venv
```
And then run
```
pip install -e . 
```
To install the `fysisk_biokemi` package and all its dependencies. 


## Rendering the exercises

To render the exercises Quarto needs to be [installed](https://quarto.org/docs/get-started/), 
a Python environment with the `fysisk_biokemi` package all needs to be active

To render the full site, navigate to the course directory and use `make` like so; 
```bash
source .venv/bin/activate # To activate the Python environment if installed like above.
cd course/
make website
```
It will start printing stuff and after ~3 minutes it should have finished and 
all the files are in `_site_combined`. The `index.html` file can be opened in a browser 
to preview the website. 

## More

- For authoring or updating exercises see [authoring.md](course/authoring.md).
- For things related to `git`, including how the website is build and hosted, see [git.md](git.md)



