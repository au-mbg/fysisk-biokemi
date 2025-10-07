import ipywidgets as widgets
from IPython.display import display, Math
from fysisk_biokemi.widgets.utils import StrictFloatText, number_to_scientific_latex
from .solution_helper import ValueWithUnit

VOLUME_FACTORS = {
    "L": 1.0,
    "mL": 1e-3,
    "µL": 1e-6,
    "nL": 1e-9,
}

CONCENTRATION_FACTORS = {
    "M": 1.0,
    "mM": 1e-3,
    "µM": 1e-6,
    "nM": 1e-9,    
}


class DilutionHelper:
    def __init__(self):
        self.stock_conc = StrictFloatText(
            description="Stock concentration",
            value="1.0",
        )

        self.stock_conc_unit = widgets.Dropdown(
            description="Unit",
            options=CONCENTRATION_FACTORS.keys(),
            value="mM",
        )

        self.final_conc = StrictFloatText(
            description="Final concentration",
            value="0.1",
        )
        self.final_conc_unit = widgets.Dropdown(
            description="Unit",
            options=CONCENTRATION_FACTORS.keys(),
            value="mM",
        )
        self.final_vol = StrictFloatText(
            description="Final volume",
            value="1.0",
        )
        self.final_vol_unit = widgets.Dropdown(
            description="Unit",
            options=VOLUME_FACTORS.keys(),
            value="mL",
        )

        self.volume_output_unit = widgets.Dropdown(
            description="Output unit",
            options=VOLUME_FACTORS.keys(),
            value="mL",
        )

        self.output = widgets.Output()

        _widgets = [
            self.stock_conc,
            self.stock_conc_unit,
            self.final_conc,
            self.final_conc_unit,
            self.final_vol,
            self.final_vol_unit,
            self.volume_output_unit,
        ]
        for w in _widgets:
            w.observe(self._on_change, names="value")

        self._on_change(None)

    def display(self):
        input_widgets = widgets.VBox(
            [
                widgets.HBox([self.stock_conc, self.stock_conc_unit]),
                widgets.HBox([self.final_conc, self.final_conc_unit]),
                widgets.HBox([self.final_vol, self.final_vol_unit]),
                self.volume_output_unit,
            ]
        )

        widget = widgets.VBox([input_widgets, self.output])
        display(widget)

    def _on_change(self, change):
        with self.output:
            self.output.clear_output()
        try:
            self._calculate()
        except Exception as e:
            with self.output:
                print(f"Error: {e}")

    def _calculate(self):
        stock_conc = ValueWithUnit(self.stock_conc.value * CONCENTRATION_FACTORS[self.stock_conc_unit.value], "M")
        final_conc = ValueWithUnit(self.final_conc.value * CONCENTRATION_FACTORS[self.final_conc_unit.value], "M")
        final_vol = ValueWithUnit(self.final_vol.value * VOLUME_FACTORS[self.final_vol_unit.value], "L")

        vol_stock = ValueWithUnit((final_conc.value * final_vol.value) / stock_conc.value, "L")
        vol_stock_in_unit = ValueWithUnit(vol_stock.value / VOLUME_FACTORS[self.volume_output_unit.value], self.volume_output_unit.value)

        vol_diluent = ValueWithUnit(final_vol.value - vol_stock.value, "L")
        vol_diluent_in_unit = ValueWithUnit(vol_diluent.value / VOLUME_FACTORS[self.volume_output_unit.value], self.volume_output_unit.value)

        # C1 V1 = C2 V2
        # V1 = (C2 V2) / C1

        line1 = r"\mathrm{{V}}_\mathrm{{stock}} &= \frac{{\mathrm{{C}}_\mathrm{{final}} \cdot \mathrm{{V}}_\mathrm{{final}}}}{{\mathrm{{C}}_\mathrm{{stock}}}}"
        line2 = rf"&= \frac{{{final_conc.repru} \cdot {final_vol.repru}}}{{{stock_conc.repru}}}"
        line3 = rf"&= \left(\frac{{{final_conc.repr} \cdot {final_vol.repr}}}{{{stock_conc.repr}}}\right) \ \frac{{{final_conc.unit_repr} \cdot {final_vol.unit_repr}}}{{{stock_conc.unit_repr}}}"
        raw = fr"""
        \begin{{aligned}}
        {line1} \\
        {line2} \\
        {line3} \\
        & = {vol_stock.repru} = {vol_stock_in_unit.repru} \\
        \end{{aligned}}
        """

        line1 = r"\mathrm{{V}}_\mathrm{{diluent}} &= \mathrm{{V}}_\mathrm{{final}} - \mathrm{{V}}_\mathrm{{stock}}"
        raw2 = fr"""
        \begin{{aligned}}
        {line1} \\
        & = {vol_diluent.repru} = {vol_diluent_in_unit.repru} \\
        \end{{aligned}}
        """

        with self.output:
            display(Math(raw))
            display(Math(raw2))


def dilution_helper():
    dh = DilutionHelper()
    dh.display()