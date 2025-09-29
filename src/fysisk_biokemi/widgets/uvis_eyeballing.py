import ipywidgets as widgets
from IPython.display import display, Math
import numpy as np
from dataclasses import dataclass

import plotly.graph_objects as go
from functools import singledispatch



@dataclass
class QuadraticBindingParameters:
    P_total: float
    L_total: float
    K_D: float

    @classmethod
    def get_random(cls):
        K_D = 10
        P_total = 100
        L_total = 10
        return cls(P_total=P_total, L_total=L_total, K_D=K_D)

@dataclass    
class SingleBindingParameters:
    K_D: float
    L_min: float
    L_max: float
    log: bool

    @classmethod
    def get_random(cls):
        K_D = np.random.uniform(low=0, high=1000, size=1)[0]
        log = np.random.choice([True, False])

        if log: 
            high = 10 *K_D
        else:
            high = 5 *K_D

        L_min = 0
        L_max = np.random.uniform(low=K_D, high=high, size=1)[0]


        return cls(K_D=K_D, L_min=L_min, L_max=L_max, log=log)

@singledispatch
def calculate_fraction_bound(params, L_total):
    raise NotImplementedError(f"Unsupported type: {type(params)}")


@calculate_fraction_bound.register
def single(params: SingleBindingParameters, L_total=None) -> float:
    if L_total is None:
        raise ValueError("L_total must be provided for single binding model")
    K_D = params.K_D
    theta = L_total / (L_total + K_D)
    return theta

@calculate_fraction_bound.register
def quadratic(params: QuadraticBindingParameters, L_total=None) -> float:
    if L_total is None:
        L_total = params.L_total

    K_D = params.K_D
    P_total = params.P_total

    theta = (
        (P_total + L_total + K_D) / (2 * P_total)
        - np.sqrt((
            ((P_total + L_total + K_D) / (2 * P_total)) ** 2 
            - L_total / P_total)
        )
    )
    return theta

class EyeBallingWidget:

    def __init__(self):
        self.plot_output = widgets.Output()

        self.generate_button = widgets.Button(
            description="Generate New Data", button_style="primary"
        )
        self.generate_button.on_click(self._on_generate_button_clicked)
        self.guess_made = False

        self.guess_kd_input = widgets.FloatText(
            description="Guess K_D (µM):",
            placeholder="Enter your guess here",
            style={'description_width': 'initial'},
        )
        self.guess_kd_input.observe(self._on_guess, names='value')

        self.guess_kd_error = widgets.HTML(
            value="", placeholder="", description=""
        )

        self.total_guesses = widgets.IntText(
            description="Total Attempts:", value=0, disabled=True, style={'description_width': 'initial'})
        self.correct_guesses = widgets.IntText(
            description="Correct Attempts:", value=0, disabled=True, style={'description_width': 'initial'})

        self.params = SingleBindingParameters.get_random()
        self._make_plot()
        self._update_plot()

    def display(self):

        controls = widgets.VBox([self.generate_button, self.guess_kd_input, self.guess_kd_error, self.total_guesses, self.correct_guesses])
        plot = widgets.VBox([self.plot_output])
        widget = widgets.HBox([controls, plot])    
        display(widget)

    def _make_plot(self):
        self.fig = go.FigureWidget(layout=go.Layout(width=600, height=400))

        trace = go.Scatter(
            x=[], y=[], mode="markers", name=r"$\theta$", line=dict(width=4)
        )
        self.fig.add_trace(trace)

        with self.plot_output:
            self.plot_output.clear_output()
            display(self.fig)

    def _update_plot(self):
        if self.params.log:
            L = np.geomspace(1e-3, self.params.L_max, 25)
        else:
            L = np.linspace(self.params.L_min, self.params.L_max, 25)

        theta = calculate_fraction_bound(self.params, L_total=L) + np.random.normal(0, 0.01, size=L.shape)
        theta = np.clip(theta, 0, 1)

        self.fig.data[0].x = L
        self.fig.data[0].y = theta

        self.fig.update_layout(
            xaxis_title="Ligand Concentration [µM]",
            yaxis_title="Fraction Bound (θ)",
            yaxis_range=[-0.05, 1.05],
            title="Fraction Bound vs Ligand Concentration",
        )

        if self.params.log:
            self.fig.update_xaxes(type="log")
        else:
            self.fig.update_xaxes(type="linear")

        self.fig.update_traces()

    def _on_generate_button_clicked(self, b):
        self.params = SingleBindingParameters.get_random()
        # Reset and reactivate input
        self.guess_kd_input.value = 10.0
        self.guess_kd_input.disabled = False

        if self.guess_made:
            self.total_guesses.value -= 1 # Account for auto-increment on guess

        # Reset error message
        self.guess_kd_error.value = ""

        # Update plot
        self._update_plot()
        self.guess_made = False

    def _on_guess(self, change):
        self.guess_made = True
        kd_guess = change['new']
        if kd_guess <= 0:
            return
        
        error = np.abs(kd_guess - self.params.K_D) / self.params.K_D * 100
        self.guess_kd_error.value = f"<b>Error:</b> {error:.2f} %"
        if error < 5:
            self.guess_kd_error.value += " 🎉 Correct!"

        self.total_guesses.value += 1
        if error < 5:
            self.correct_guesses.value += 1
            self.guess_kd_input.disabled = True

class CompareSimpleVSQuadraticWidget:

    def __init__(self):

        # Controls: 
        self.k_d_input = widgets.FloatSlider(
            description="K_D (µM):",
            value=10.0,
            min=0.1,
            max=100.0, step=0.1,
            style={'description_width': 'initial'},
        )
        self.p_total_input = widgets.FloatSlider(
            description="P_total (µM):",
            value=10.0,
            min=0.1,
            max=1000.0, step=0.1,
            style={'description_width': 'initial'},
        )
        self.plot_output = widgets.Output()

        self.k_d_input.observe(self._update_plot, names='value')
        self.p_total_input.observe(self._update_plot, names='value')

    def _make_plot(self):
        self.fig = go.FigureWidget(layout=go.Layout(width=700, height=500))

        trace1 = go.Scatter(
            x=[], y=[], mode="lines", name="Simple Binding", line=dict(width=4)
        )
        trace2 = go.Scatter(
            x=[], y=[], mode="lines", name="Quadratic Binding", line=dict(width=4)
        )
        self.fig.add_trace(trace1)
        self.fig.add_trace(trace2)

        self.fig.update_layout(
            xaxis_title="Ligand Concentration [µM]",
            yaxis_title="Fraction Bound (θ)",
            yaxis_range=[-0.05, 1.05],
            title="Fraction Bound vs Ligand Concentration",
        )


        with self.plot_output:
            self.plot_output.clear_output()
            display(self.fig)

    def _update_plot(self, change=None):
        L = np.linspace(0, 10 * self.k_d_input.value, 100)

        K_D = self.k_d_input.value
        P_total = self.p_total_input.value

        simple = SingleBindingParameters(K_D=K_D, L_max=None, L_min=None, log=False)
        quad = QuadraticBindingParameters(K_D=K_D, P_total=P_total, L_total=None)

        theta_simple = calculate_fraction_bound(simple, L_total=L)
        theta_quad = calculate_fraction_bound(quad, L_total=L)

        self.fig.data[0].x = L
        self.fig.data[0].y = theta_simple
        self.fig.data[1].x = L
        self.fig.data[1].y = theta_quad

    def display(self):
        self._make_plot()
        self._update_plot()

        controls = widgets.VBox([self.k_d_input, self.p_total_input])
        plot = widgets.VBox([self.plot_output])
        widget = widgets.HBox([controls, plot])    
        display(widget)


def estimate_kd():
    widget = EyeBallingWidget()
    widget.display()

def visualize_simple_vs_quadratic():
    widget = CompareSimpleVSQuadraticWidget()
    widget.display()

