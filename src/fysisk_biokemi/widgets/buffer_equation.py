import ipywidgets as widgets
from IPython.display import display, Math
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass

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

        self.acid_conc_input = widgets.FloatText(
            description="Syre konc. (M):",
            value=0.05,
            disabled=True,
            style={"description_width": "initial", "text_align": "right"},
        )
        self.base_conc_input = widgets.FloatText(
            description="Base konc. (M):",
            value=0.05,
            disabled=True,
            style={"description_width": "initial", "text_align": "right"},
        )

        self.output_field = widgets.Output()

        self.pH_input.observe(self._on_change)
        self.pKa_input.observe(self._on_change)
        self.total_conc_input.observe(self._on_change)

    def display(self):
        widget = widgets.HBox(
            [
                widgets.VBox(
                    [
                        self.pH_input,
                        self.pKa_input,
                        self.total_conc_input,
                        self.acid_conc_input,
                        self.base_conc_input,
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
            total_conc = self.total_conc_input.value

            acid_conc, base_conc, ratio = calculate_acid_base_concentrations(pH, pKa, total_conc)

            # Update the acid and base concentration fields
            self.acid_conc_input.value = round(acid_conc, 6)
            self.base_conc_input.value = round(base_conc, 6)

            with self.output_field:
                self.output_field.clear_output()

                derivation = []

                derivation += [r"\frac{[\text{base}]}{[\text{acid}]} = 10^{\text{pH} - \text{pKa}} = " + f"{ratio:.3f}"]
                derivation += [
                    r"[\text{base}] + [\text{acid}] = C_{\text{total}} = " + rf"{total_conc:.3f} \, \text{{M}}" + r"\\"
                ]
                derivation += [
                    r"[\text{base}] = \frac{C_{\text{total}} \cdot 10^{\text{pH} - \text{pKa}}}{1 + 10^{\text{pH} - \text{pKa}}} = "
                    + rf"\underline{{{base_conc:.3f}}} \, \text{{M}}"
                    + r"\\"
                ]
                derivation += [
                    r"[\text{acid}] = C_{\text{total}} - [\text{base}] = "
                    + rf"\underline{{{acid_conc:.3f}}} \, \text{{M}}"
                ]

                for line in derivation:
                    display(Math(line))

@dataclass
class FigureAttrs:
    fig: plt.Figure
    ax: plt.Axes
    acid_line: plt.Line2D
    base_line: plt.Line2D
    pka_line: plt.Line2D


class BufferVisualization:
    def __init__(self):
        self.pka_input = widgets.FloatSlider(
            value=7.0, min=0.0, max=14.0, step=0.1, description="pKa:", style={"description_width": "initial"}
        )
        self.total_conc_input = widgets.FloatSlider(
            value=0.1,
            min=0.01,
            max=1.0,
            step=0.01,
            description="Total koncentration (M):",
            style={"description_width": "initial"},
        )

        self.ph_range_input = widgets.FloatRangeSlider(
            value=[5.0, 9.0],
            min=0.0,
            max=14.0,
            step=0.1,
            description="pH-område:",
            style={"description_width": "initial"},
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

    def make_plot(self, ph, acid, base, pka_value):
        fig, ax = plt.subplots(figsize=(6, 4))
        acid_line, = ax.plot(ph, acid, label="Syre [M]", color="blue")
        base_line, = ax.plot(ph, base, label="Base [M]", color="orange")
        pka_line = ax.axvline(pka_value, color="green", linestyle="--", label="pKa")
        ax.set_title("Buffer Sammensætning vs pH")
        ax.set_xlabel("pH")
        ax.set_ylabel("Koncentration [M]")
        ax.legend()
        ax.grid()
        return FigureAttrs(fig, ax, acid_line, base_line, pka_line)
    
    def update_plot(self, ph, acid, base, pka_value):
        self.plot_attrs.acid_line.set_data(ph, acid)
        self.plot_attrs.base_line.set_data(ph, base)
        self.plot_attrs.pka_line.set_xdata([pka_value, pka_value])
        self.plot_attrs.ax.relim()
        self.plot_attrs.ax.autoscale_view()
        self.plot_attrs.fig.canvas.draw_idle()


    def _on_change(self, change):
        pka_value = self.pka_input.value
        total_conc_value = self.total_conc_input.value
        pH_range = self.ph_range_input.value

        ph = np.linspace(pH_range[0], pH_range[1], 400)
        acid, base, ratio = calculate_acid_base_concentrations(ph, pka_value, total_conc_value)


        # Initialize the plot if it hasn't been created yet
        if not hasattr(self, 'plot_attrs'):
            with self.plot_output:
                self.plot_output.clear_output()
                self.plot_attrs = self.make_plot(ph, acid, base, pka_value)
                plt.show()

        # Update the plot data
        with self.plot_output:
            self.plot_output.clear_output()
            self.update_plot(ph, acid, base, pka_value)
            display(self.plot_attrs.fig)









def buffer_equation():
    be = BufferEquation()
    be._on_change({"type": "change", "name": "value", "new": None})
    be.display()

def buffer_visualization():
    bv = BufferVisualization()
    bv._on_change({"type": "change", "name": "value", "new": None})
    bv.display()