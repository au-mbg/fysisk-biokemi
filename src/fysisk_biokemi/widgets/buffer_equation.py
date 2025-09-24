import ipywidgets as widgets
from IPython.display import display, Math
import numpy as np
from dataclasses import dataclass
import plotly.graph_objects as go

from fysisk_biokemi.widgets.utils import molar_prefix_to_factor, number_to_scientific_latex


def calculate_acid_base_concentrations(pH, pKa, total_conc):
    ratio = 10 ** (pH - pKa)
    base_conc = (total_conc * ratio) / (1 + ratio)
    acid_conc = total_conc - base_conc
    return acid_conc, base_conc, ratio


class BufferEquation:
    def __init__(self):
        self.pH_input = widgets.FloatText(description="pH:", value=7.0, style={"description_width": "initial"})
        self.pKa_input = widgets.FloatText(description="pKa:", value=7.0, style={"description_width": "initial"})

        self.total_conc_input = widgets.FloatText(
            description="Total koncentration (M):", value=0.1, style={"description_width": "initial"}
        )

        self.concentration_unit = widgets.Dropdown(
            options=list(molar_prefix_to_factor.keys()),
            value="M",
            description="Konc. enhed:",
        )

        self.output_field = widgets.Output()

        self.pH_input.observe(self._on_change)
        self.pKa_input.observe(self._on_change)
        self.total_conc_input.observe(self._on_change)
        self.concentration_unit.observe(self._on_change)

    def display(self):
        widget = widgets.HBox(
            [
                widgets.VBox(
                    [
                        self.pH_input,
                        self.pKa_input,
                        self.total_conc_input, 
                        self.concentration_unit,
                    ]
                ),
                self.output_field,
            ]
        )
        display(widget)

    def _on_change(self, change):
        if change["type"] == "change" and change["name"] == "value":
            pH = self.pH_input.value
            pKa = self.pKa_input.value
            total_conc = self.total_conc_input.value * molar_prefix_to_factor[self.concentration_unit.value]

            acid_conc, base_conc, ratio = calculate_acid_base_concentrations(pH, pKa, total_conc)

            with self.output_field:
                self.output_field.clear_output()

                derivation = []

                derivation += [r"\frac{[\text{base}]}{[\text{acid}]} = 10^{\text{pH} - \text{pKa}} = " + f"{number_to_scientific_latex(ratio)}"]
                derivation += [
                    r"[\text{base}] + [\text{acid}] = C_{\text{total}} = " + rf"{number_to_scientific_latex(total_conc)} \, \text{{M}}" + r"\\"
                ]
                derivation += [
                    r"[\text{base}] = \frac{C_{\text{total}} \cdot 10^{\text{pH} - \text{pKa}}}{1 + 10^{\text{pH} - \text{pKa}}} = "
                    + rf"\underline{{{number_to_scientific_latex(base_conc)}}} \, \text{{M}}"
                    + r"\\"
                ]
                derivation += [
                    r"[\text{acid}] = C_{\text{total}} - [\text{base}] = "
                    + rf"\underline{{{number_to_scientific_latex(acid_conc)}}} \, \text{{M}}"
                ]

                for line in derivation:
                    display(Math(line))


@dataclass
class FigureAttrs:
    fig: go.FigureWidget
    acid_idx: int
    base_idx: int
    pka_shape_idx: int  # index in fig.layout.shapes

class BufferVisualization:
    def __init__(self, continuous_update: bool = True):
        self.continuous_update = continuous_update

        self.pka_input = widgets.FloatSlider(
            value=7.0, min=0.0, max=14.0, step=0.1, description="pKa:", style={"description_width": "initial"},
            continuous_update=continuous_update,
        )
        self.total_conc_input = widgets.FloatSlider(
            value=0.1,
            min=0.01,
            max=1.0,
            step=0.01,
            description="Total koncentration (M):",
            style={"description_width": "initial"},
            continuous_update=continuous_update,
        )

        self.ph_range_input = widgets.FloatRangeSlider(
            value=[5.0, 9.0],
            min=0.0,
            max=14.0,
            step=0.1,
            description="pH-område:",
            style={"description_width": "initial"},
            continuous_update=continuous_update,
        )

        self.plot_output = widgets.Output()

    def display(self):
        controls = widgets.VBox(
            [
                self.pka_input,
                self.total_conc_input,
                self.ph_range_input,
            ]
        )

        self.pka_input.observe(self._on_change)
        self.total_conc_input.observe(self._on_change)
        self.ph_range_input.observe(self._on_change)
        widget = widgets.HBox([controls, self.plot_output])
        display(widget)

    def make_plot(self, ph, acid, base, pka_value) -> FigureAttrs:
        fig = go.FigureWidget(layout=go.Layout(width=600, height=400))

        acid_trace = go.Scatter(x=ph, y=acid, mode="lines", name="Syre [M]", line=dict(width=4))
        base_trace = go.Scatter(x=ph, y=base, mode="lines", name="Base [M]", line=dict(width=4))

        fig.add_traces([acid_trace, base_trace])

        # Vertical pKa line as a shape (dragging-safe and efficient)
        fig.update_layout(
            title="Buffer Sammensætning vs pH",
            xaxis_title="pH",
            yaxis_title="Koncentration [M]",
            template="plotly_white",
            legend=dict(orientation="v", yanchor="bottom", y=0.9, xanchor="right", x=0.95),
            margin=dict(l=60, r=20, t=50, b=40),
        )
        fig.add_vline(x=pka_value, line_dash="dash", line_color="green", annotation_text="pKa", annotation_position="top")

        with self.plot_output:
            self.plot_output.clear_output(wait=True)
            display(fig)

        # Store indices for fast updates
        acid_idx = 0
        base_idx = 1
        pka_shape_idx = len(fig.layout.shapes) - 1 if fig.layout.shapes else 0

        return FigureAttrs(fig=fig, acid_idx=acid_idx, base_idx=base_idx, pka_shape_idx=pka_shape_idx)

    def update_plot(self, ph, acid, base, pka_value):
        fa = self.plot_attrs
        # Update data
        fa.fig.data[fa.acid_idx].x = ph
        fa.fig.data[fa.acid_idx].y = acid
        fa.fig.data[fa.base_idx].x = ph
        fa.fig.data[fa.base_idx].y = base

        # Update vertical pKa line (shape)
        shp = fa.fig.layout.shapes[fa.pka_shape_idx]
        shp.update(x0=pka_value, x1=pka_value)

        # Optionally tighten y-range around current data
        # (Plotly autoscale is automatic on first draw; for dynamic:
        y_min = float(np.nanmin([acid.min(), base.min(), 0]))
        y_max = float(np.nanmax([acid.max(), base.max()])) * 1.05 if np.isfinite([acid.max(), base.max()]).all() else 1
        fa.fig.update_yaxes(range=[y_min, y_max])

    def _on_change(self, change):
        pka_value = self.pka_input.value
        total_conc_value = self.total_conc_input.value
        pH_range = self.ph_range_input.value

        ph = np.linspace(pH_range[0], pH_range[1], 400)
        acid, base, ratio = calculate_acid_base_concentrations(ph, pka_value, total_conc_value)

        # Initialize the plot if it hasn't been created yet
        if not hasattr(self, "plot_attrs"):
            self.plot_attrs = self.make_plot(ph, acid, base, pka_value)
            return

        # Update
        self.update_plot(ph, acid, base, pka_value)


def buffer_equation():
    be = BufferEquation()
    be._on_change({"type": "change", "name": "value", "new": None})
    be.display()


def buffer_visualization(continuous_update: bool = True):
    bv = BufferVisualization(continuous_update=continuous_update)
    bv._on_change({"type": "change", "name": "value", "new": None})
    bv.display()

if __name__ == "__main__":
    buffer_visualization()