import ipywidgets as widgets
from IPython.display import display, Math
from fysisk_biokemi.widgets.utils import ATOMIC_WEIGHTS


def formula_to_weight(formula: str) -> float:
    import re

    pattern = r"([A-Z][a-z]?)(\d*\.?\d*)"
    matches = re.findall(pattern, formula)
    weight = 0.0
    for element, count in matches:
        if element not in ATOMIC_WEIGHTS:
            return float("nan")
        atomic_weight = ATOMIC_WEIGHTS[element]
        count = float(count) if count else 1.0
        weight += atomic_weight * count
    return weight


def molecular_weight():
    formula_input = widgets.Text(description="Formel:", value="C6H12O6", style={"description_width": "initial"})
    weight_output = widgets.FloatText(
        description="Mol.vægt (g/mol):",
        value=180.16,
        disabled=True,
        style={"description_width": "initial", "text_align": "right"},
    )

    def update(*args):
        formula = formula_input.value
        weight = formula_to_weight(formula)
        weight_output.value = weight

    formula_input.observe(update, names="value")

    ui = widgets.VBox([formula_input, weight_output])
    display(ui)
    update()
