import ipywidgets as widgets
from IPython.display import display, Math
from fysisk_biokemi.widgets.utils import StrictFloatText, number_to_scientific_latex

# --- unit factors ---
MASS_FACTORS = {
    "g": 1.0,
    "mg": 1e-3,
    "µg": 1e-6,
    "ng": 1e-9,
}

VOLUME_FACTORS = {
    "L": 1.0,
    "mL": 1e-3,
    "µL": 1e-6,
}

CONCENTRATION_FACTORS = {
    "M": 1.0,
    "mM": 1e-3,
    "µM": 1e-6,
    "nM": 1e-9,
}

MOLECULAR_WEIGHT_FACTORS = {
    "g/mol": 1.0,
    "kg/mol": 1e3,
    "Da": 1.0,
    "kDa": 1e3,
}

class ValueWithUnit:

    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    @property
    def repr(self):
        if self.value < 1e-3 or self.value > 1e3:
            rep = f"{number_to_scientific_latex(self.value)}"
        else:
            rep = f"{self.value:.3f}"

        return rep
    @property
    def repru(self):
        return f"{self.repr} \ {self.unit_repr}"

    @property    
    def unit_repr(self):
        if "/" in self.unit:
            num, denom = self.unit.split("/")
            return rf"\frac{{\mathrm{{{num}}}}}{{\mathrm{{{denom}}}}}"

        return f"\mathrm{{{self.unit}}}"
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.value * other
        raise NotImplementedError("Can only multiply ValueWithUnit by int or float")


class SolutionHelper:
    def __init__(self, options=None, shown_options=None):

        if options is None:
            options = ["Masse", "Koncentration"]
        else:
            for opt in options:
                if opt not in ["Masse", "Koncentration", "Volumen", "Mol.vægt"]:
                    raise ValueError(f"Unknown option: {opt}")
        self.options = options

        # Shown options:
        if shown_options is None:
            self.shown_options = ["Masse", "Koncentration", "Volumen", "Mol.vægt"]
        else:
            self.shown_options = shown_options
        for opt in self.shown_options:
            if opt not in ["Masse", "Koncentration", "Volumen", "Mol.vægt"]:
                raise ValueError(f"Unknown shown_option: {opt}")

        # Input widgets:
        self.mass_value = StrictFloatText(description="Masse:", value="70.0")
        self.concentration_value = StrictFloatText(description="Koncentration (M):", value="1.0")
        self.volume_value = StrictFloatText(description="Volumen:", value="1.0")
        self.mol_weight_value = StrictFloatText(
            description="Mol.vægt:", value="190000.0", style={"description_width": "initial"}
        )

        # Buttons to select which is active:
        self.buttons = widgets.ToggleButtons(
            options=options,
            description="Beregn:",
            button_style="info",
            tooltips=[
                "Beregn masse (g)",
                "Beregn koncentration (M)",
            ],
        )
        # Enheder
        self.mass_unit = widgets.Dropdown(description="Enhed:", options=MASS_FACTORS.keys(), value="g")
        self.volume_unit = widgets.Dropdown(description="Enhed:", options=VOLUME_FACTORS.keys(), value="L")
        self.concentration_unit = widgets.Dropdown(
            description="Enhed:", options=CONCENTRATION_FACTORS.keys(), value="M"
        )
        self.mol_weight_unit = widgets.Dropdown(
            description="Enhed:", options=MOLECULAR_WEIGHT_FACTORS.keys(), value="g/mol"
        )

        # Output widget - Justify center
        self.output = widgets.Output()

        # Observe changes:
        _widgets = [
            self.mass_value,
            self.concentration_value,
            self.volume_value,
            self.mol_weight_value,
            self.mass_unit,
            self.volume_unit,
            self.concentration_unit,
            self.mol_weight_unit,
            self.buttons,
        ]
        for w in _widgets:
            w.observe(self._on_change, names="value")

        self._on_change(None)  # Initialize state

    def display(self):

        placeholder = widgets.HTML()
        inputs = widgets.VBox(
            [
                widgets.HTML(value="<b>Input:</b>"),
                widgets.HBox([self.mass_value, self.mass_unit]) if "Masse" in self.shown_options else placeholder,
                widgets.HBox([self.concentration_value, self.concentration_unit]) if "Koncentration" in self.shown_options else placeholder,
                widgets.HBox([self.volume_value, self.volume_unit]) if "Volumen" in self.shown_options else placeholder,
                widgets.HBox([self.mol_weight_value, self.mol_weight_unit]) if "Mol.vægt" in self.shown_options else placeholder,
            ]
        )

        if len(self.options) > 1:
            inputs.children = inputs.children + (self.buttons,)


        widget = widgets.VBox([inputs, self.output])
        display(widget)

    def _on_change(self, change):
        # Which is active button?
        mode = self.buttons.value
        self._deactivate(mode)

        with self.output:
            self.output.clear_output()

            display(widgets.HTML(value="<b>Udregning:</b>"))

            if mode == "Masse":
                latex = self._calculate_mass()
            elif mode == "Koncentration":
                latex = self._calculate_concentration()
            elif mode == "Volumen":
                latex = self._calculate_volume()

            display(latex)

    def _deactivate(self, to_calculate):
        # Deactivate the input for the one to calculate:
        self.mass_value.disabled = to_calculate == "Masse"
        self.concentration_value.disabled = to_calculate == "Koncentration"
        self.volume_value.disabled = to_calculate == "Volumen"
        self.mol_weight_value.disabled = to_calculate == "Mol.vægt"

    def _calculate_mass(self):
        # m = c * V * MW
        c = ValueWithUnit(self.concentration_value.value * CONCENTRATION_FACTORS[self.concentration_unit.value], "M")
        V = ValueWithUnit(self.volume_value.value * VOLUME_FACTORS[self.volume_unit.value], "L")
        MW = ValueWithUnit(self.mol_weight_value.value * MOLECULAR_WEIGHT_FACTORS[self.mol_weight_unit.value], "g/mol")
        m = c.value * V.value * MW.value  # g
        m = m / MASS_FACTORS[self.mass_unit.value]
        m = ValueWithUnit(m, self.mass_unit.value)
        unit_calc = r"\frac{\cancel{\mathrm{mol}}\cdot \cancel{\mathrm{L}}\cdot \mathrm{g}}{\cancel{\mathrm{L}}\cdot\cancel{\mathrm{mol}}}"

        # LateX
        raw = fr"""
        \begin{{aligned}}
        m & = c \cdot V \cdot M_W \\ 
        & = {c.repru} \cdot {V.repru} \cdot {MW.repru} \\
        & = {c.repr} \cdot {V.repr} \cdot {MW.repr} \ {c.unit_repr}\cdot{V.unit_repr}\cdot{MW.unit_repr} \\
        & = {m.repr} \ {unit_calc} \\
        & = {m.repru}
        \end{{aligned}}
        """
        latex = Math(raw)

        return latex
    
    def _calculate_concentration(self):
        # c = m / (V * MW)
        m = ValueWithUnit(self.mass_value.value * MASS_FACTORS[self.mass_unit.value], "g")
        V = ValueWithUnit(self.volume_value.value * VOLUME_FACTORS[self.volume_unit.value], "L")
        MW = ValueWithUnit(self.mol_weight_value.value * MOLECULAR_WEIGHT_FACTORS[self.mol_weight_unit.value], "g/mol")
        c = m.value / (V.value * MW.value)  # M
        c = c / CONCENTRATION_FACTORS[self.concentration_unit.value]
        c = ValueWithUnit(c, self.concentration_unit.value)

        unit_calc = r"\frac{\cancel{\mathrm{g}}\cdot\mathrm{mol}}{\mathrm{L}\cdot\cancel{\mathrm{g}}}"

        # LateX
        raw = fr"""
        \begin{{aligned}}
        c & = \frac{{m}}{{V \cdot M_W}} \\ 
        & = \frac{{{m.repru}}}{{{V.repru} \cdot {MW.repru}}} \\
        & = \frac{{{m.repr}}}{{{V.repr} \cdot {MW.repr}}} \cdot \frac{{{m.unit_repr}}}{{{V.unit_repr} \cdot {MW.unit_repr}}} \\
        & = {c.repr} \ {unit_calc} \\
        & = {c.repru}
        \end{{aligned}}
        """
        latex = Math(raw)

        return latex
    
    def _calculate_volume(self):
        # V = m / (c * MW)
        m = ValueWithUnit(self.mass_value.value * MASS_FACTORS[self.mass_unit.value], "g")
        c = ValueWithUnit(self.concentration_value.value * CONCENTRATION_FACTORS[self.concentration_unit.value], "M")
        MW = ValueWithUnit(self.mol_weight_value.value * MOLECULAR_WEIGHT_FACTORS[self.mol_weight_unit.value], "g/mol")
        V = m.value / (c.value * MW.value)  # L
        V = V / VOLUME_FACTORS[self.volume_unit.value]
        V = ValueWithUnit(V, self.volume_unit.value)

        unit_calc = r"\frac{\cancel{\mathrm{g}} \cdot \mathrm{L} \cdot \cancel{\mathrm{mol}}}{\cancel{\mathrm{mol}} \cdot \cancel{\mathrm{g}}}"

        # LateX
        raw = fr"""
        \begin{{aligned}}
        V & = \frac{{m}}{{c \cdot M_W}} \\ 
        & = \frac{{{m.repru}}}{{{c.repru} \cdot {MW.repru}}} \\
        & = \frac{{{m.repr}}}{{{c.repr} \cdot {MW.repr}}} \cdot \frac{{{m.unit_repr}}}{{{c.unit_repr} \cdot {MW.unit_repr}}} \\
        & = {V.repr} \ {unit_calc} \\
        & = {V.repru}
        \end{{aligned}}
        """
        latex = Math(raw)

        return latex

def solution_helper():
    sh = SolutionHelper()
    sh.display()

def concentration_mass_volume():
    sh = SolutionHelper(options=["Koncentration"], shown_options=["Masse", "Volumen", "Mol.vægt"])
    sh.display()

def mass_concentration_volume():
    sh = SolutionHelper(options=["Masse"], shown_options=["Koncentration", "Volumen", "Mol.vægt"])
    sh.display()