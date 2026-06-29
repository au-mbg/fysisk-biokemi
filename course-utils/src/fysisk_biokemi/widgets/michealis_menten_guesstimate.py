import ipywidgets as widgets
from IPython.display import display
import numpy as np
from dataclasses import dataclass

import plotly.graph_objects as go

@dataclass
class MichealisMentenParameters:
    Vmax: float
    Km: float
    log: bool
    n_points: int

    @staticmethod
    def get_random():
        Vmax = np.random.uniform(50, 200)
        Km = np.random.uniform(5, 100)
        log = np.random.choice([True, False])
        n_points = np.random.randint(5, 50)
        return MichealisMentenParameters(Vmax=Vmax, Km=Km, log=log, n_points=n_points)


class MichealisMentenGuesstimateWidget:

    def __init__(self, correct_threshold=10.0, debug=False):
        self.plot_output = widgets.Output()
        self.error_output = widgets.Output()

        # Generate data button
        self.generate_button = widgets.Button(
            description="Generate New Data", button_style="primary"
        )
        self.generate_button.on_click(self._on_generate_button_clicked)
        self.guess_made = False

        # Guess Vmax
        self.guess_vmax_input = widgets.FloatText(
            description="Guess Vmax (M/s):",
            placeholder="Enter your guess here",
            style={'description_width': 'initial'},
        )
        self.guess_vmax_input.observe(self._on_guess_vmax, names='value')

        self.guess_vmax_error = widgets.HTML(
            value="", placeholder="", description=""
        )

        ## Guess Km
        self.guess_km_input = widgets.FloatText(
            description="Guess K_M (M):",
            placeholder="Enter your guess here",
            style={'description_width': 'initial'},
        )
        self.guess_km_input.observe(self._on_guess_km, names='value')

        self.guess_km_error = widgets.HTML(
            value="", placeholder="", description=""
        )

        # Set correct threshold & initial parameters
        self.correct_threshold = correct_threshold
        self.parameters = MichealisMentenParameters.get_random()

        if debug:
            self.debug_output = widgets.Output()            
        else:
            self.debug_output = None


    def display(self):
        self._make_plot()
        controls = widgets.VBox([self.generate_button, self.guess_vmax_input, self.guess_vmax_error, self.guess_km_input, self.guess_km_error])
        if self.debug_output is not None:
            widget = widgets.HBox([controls, self.plot_output, self.error_output, self.debug_output])    
        else:
            widget = widgets.HBox([controls, self.plot_output, self.error_output])
        display(widget)

    def _get_data(self):

        if self.parameters.log:
            L = np.logspace(0, 3, self.parameters.n_points)
        else:
            L = np.linspace(0, 1000, self.parameters.n_points)

        V0 = (self.parameters.Vmax * L) / (self.parameters.Km + L)
        return L, V0

    def _make_plot(self):
        self.fig = go.FigureWidget(layout=go.Layout(width=600, height=400))

        x, y = self._get_data()

        trace = go.Scatter(
            x=x, y=y, mode="markers", name=r"$V0$", line=dict(width=4)
        )
        self.fig.add_trace(trace)
        self.fig.update_layout(
            title="Estimate Michealis-Menten Parameters",
            template="plotly_white",
            xaxis_title="[S] (M)",
            yaxis_title=r"V0 (M/s)",

        )

        with self.plot_output:
            self.plot_output.clear_output()
            display(self.fig)

    def _update_plot(self):

        L, theta = self._get_data()

        self.fig.data[0].x = L
        self.fig.data[0].y = theta

        if self.parameters.log:
            self.fig.update_xaxes(type="log")
        else:
            self.fig.update_xaxes(type="linear")

    def _on_generate_button_clicked(self, b):
        self.parameters = MichealisMentenParameters.get_random()
        # Update plot

        if self.debug_output is not None:
            with self.debug_output:
                self.debug_output.clear_output()
                print(f"DEBUG: Vmax = {self.parameters.Vmax:.2f}, Km = {self.parameters.Km:.2f}, log = {self.parameters.log}, n_points = {self.parameters.n_points}")

        self._update_plot()

    def _on_guess_km(self, change):
        self.guess_made = True
        km_guess = change['new']
        if km_guess <= 0:
            return
        
        error = np.abs(km_guess - self.parameters.Km) / self.parameters.Km * 100
        self.guess_km_error.value = f"<b>Error:</b> {error:.2f} %"
        if error < self.correct_threshold:
            self.guess_km_error.value += " 🎉 Correct!"

    def _on_guess_vmax(self, change):
        self.guess_made = True
        vmax_guess = change['new']
        if vmax_guess <= 0:
            return
        
        error = np.abs(vmax_guess - self.parameters.Vmax) / self.parameters.Vmax * 100
        self.guess_vmax_error.value = f"<b>Error:</b> {error:.2f} %"
        if error < self.correct_threshold:
            self.guess_vmax_error.value += " 🎉 Correct!"

def michealis_menten_guess(debug=False):
    widget = MichealisMentenGuesstimateWidget(debug=debug)
    widget.display()
