import ipywidgets as widgets
from IPython.display import display, Math
import numpy as np
from dataclasses import dataclass

import plotly.graph_objects as go


class MichaelisMenten:
    def __init__(self):
        # Inputs:
        self.km_input = widgets.FloatSlider(value=5, min=0.1, max=50.0, step=0.1, description="Km:", disabled=False)

        self.vmax_input = widgets.FloatSlider(value=30, min=1, max=1000.0, step=1, description="Vmax:", disabled=False)

        self.enzyme_conc = widgets.FloatText(value=0.0005, description="[Etot]:", disabled=False, step=0.1)

        self.substrate_range = widgets.FloatRangeSlider(
            value=[0.0, 100.0], min=0.0, max=100.0, step=1, description="[S] range:", disabled=False
        )

        self.substrate_measurements = widgets.IntSlider(
            value=50, min=5, max=100, step=1, description="Data points:", disabled=False
        )

        self.noise_input = widgets.FloatText(value=0.01, description="Noise level:", disabled=False, step=0.1)

        # Controls:
        self.noise_active = widgets.Checkbox(value=False, description="Add noise:", disabled=False, indent=False)
        self.plot_lines = widgets.Checkbox(value=True, description="Show lines", disabled=False, indent=False)
        self.show_km = widgets.Checkbox(value=False, description="Show Km", disabled=False, indent=False)
        self.show_vmax = widgets.Checkbox(value=False, description="Show Vmax", disabled=False, indent=False)

        # Outputs:
        self.plot_output = widgets.Output()
        self.text_output = widgets.Output()

        # Observe changes
        self.km_input.observe(self._on_change, names="value")
        self.vmax_input.observe(self._on_change, names="value")
        self.substrate_range.observe(self._on_change, names="value")
        self.noise_active.observe(self._on_change, names="value")
        self.noise_input.observe(self._on_change, names="value")
        self.plot_lines.observe(self._on_change, names="value")
        self.substrate_measurements.observe(self._on_change, names="value")
        self.show_km.observe(self._on_change, names="value")
        self.show_vmax.observe(self._on_change, names="value")
        self.enzyme_conc.observe(self._on_change, names="value")

    def calculate(self):
        km = self.km_input.value
        vmax = self.vmax_input.value
        s_min, s_max = self.substrate_range.value
        noise_level = self.noise_input.value

        s_values = np.linspace(s_min, s_max, self.substrate_measurements.value)
        v_values = (vmax * s_values) / (km + s_values)
        if self.noise_active.value:
            noise = np.random.normal(0, noise_level, size=v_values.shape)
            v_values += noise

        return s_values, v_values

    def _make_plot(self):
        s_values, v_values = self.calculate()
        fig = go.FigureWidget(layout=go.Layout(width=800, height=600))
        # Data trace
        fig.add_trace(go.Scatter(x=s_values, y=v_values, mode="lines+markers", name="Data"))

        # Km line
        fig.add_trace(
            go.Scatter(
                x=[self.km_input.value, self.km_input.value],
                y=[0, self.vmax_input.value / 2],
                mode="lines",
                line=dict(dash="dash", color="red"),
                name="Km",
                visible=self.show_km.value,
            )
        )

        # Vmax line
        fig.add_trace(
            go.Scatter(
                x=[0, self.substrate_range.value[1]],
                y=[self.vmax_input.value, self.vmax_input.value],
                mode="lines",
                line=dict(dash="dash", color="green"),
                name="Vmax",
                visible=self.show_vmax.value,
            )
        )

        fig.add_annotation(
            x=0.60, y=0.02, xref="paper", yref="paper",  # relative to the plotting area
            xanchor="left", yanchor="bottom",
            text="",
            showarrow=False,
            align="left",
            font=dict(size=14)
        )

        fig.add_annotation(
            x=0.60, y=0.16, xref="paper", yref="paper",  # relative to the plotting area
            xanchor="left", yanchor="bottom",
            text="",
            showarrow=False,
            align="left",
            font=dict(size=14)
        )
        

        fig.update_layout(
            title="Michaelis-Menten Kinetics",
            xaxis_title="[S] (Substrate Concentration)",
            yaxis_title="v (Reaction Velocity)",
            width=600,
            height=400,
        )

        return fig

    def _update_plot(self):
        s, v = self.calculate()
        with self.fig.batch_update():
            self.fig.data[0].x = s
            self.fig.data[0].y = v

            if self.plot_lines.value:
                self.fig.data[0].mode = "lines+markers"
            else:
                self.fig.data[0].mode = "markers"

            # Km line
            self.fig.data[1].x = [self.km_input.value, self.km_input.value]
            self.fig.data[1].y = [0, self.vmax_input.value / 2]
            self.fig.data[1].visible = self.show_km.value

            # Vmax line
            self.fig.data[2].x = [0, self.substrate_range.value[1]]
            self.fig.data[2].y = [self.vmax_input.value, self.vmax_input.value]
            self.fig.data[2].visible = self.show_vmax.value

    def _on_change(self, change):
        try:
            self._update_plot()

            with self.text_output:
                self.text_output.clear_output(wait=True)
                km = self.km_input.value
                vmax = self.vmax_input.value
                etot = self.enzyme_conc.value
                kcat = vmax / etot
                kcat_km = kcat / km 

                k_cat_str = r"$k_{{cat}} = \frac{{V_{{max}}}}{{[E]_{{tot}}}} = {:.2f}$".format(kcat)
                k_cat_km_str = r"$\frac{{k_{{cat}}}}{{K_m}} = {:.2f}$".format(kcat_km)
                self.fig.layout.annotations[0].text = k_cat_str
                self.fig.layout.annotations[1].text = k_cat_km_str
        except Exception as e:
            pass

    def display(self):
        # Controls
        input_label = widgets.HTML(value="<b>Input parameters:</b>")
        inputs = [
            self.km_input,
            self.vmax_input,
            self.enzyme_conc,
            self.substrate_range,
            self.substrate_measurements,
            self.noise_input,
        ]
        button_labels = widgets.HTML("<b>Controls</b>")
        buttons = [self.noise_active, self.plot_lines, self.show_km, self.show_vmax]

        controls = widgets.VBox(
            [
                input_label,
                *inputs,
                button_labels,
                *buttons,
            ],
        )

        # Initial plot
        with self.plot_output:
            self.plot_output.clear_output(wait=True)
            self.fig = self._make_plot()
            display(self.fig)

        widget = widgets.HBox([controls, self.plot_output]) #self.text_output])
        display(widget)

        self._on_change(None)

def michaelis_menten_demo():
    widget = MichaelisMenten()
    widget.display()
    widget.km_input.value = 0.5 # This seems to stop the widget from throwing useless errors.