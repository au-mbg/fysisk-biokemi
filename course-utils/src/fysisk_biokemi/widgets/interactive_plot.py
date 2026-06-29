import numpy as np
import ipywidgets as widgets
import plotly.graph_objects as go
from dataclasses import dataclass
from IPython.display import display, Math


@dataclass
class PlotConfig:
    function: callable
    parameters: dict
    parameter_ranges: dict
    independent_range: tuple
    xlabel: str
    ylabel: str
    title: str = "Interactive Plot"
    latex_str: str | None = None
    parameters_latex: dict | None = None


class ParameterControl:
    def __init__(self, name, value, min_val, max_val, step, latex_label=None):
        self.name = name
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.latex_label = latex_label if latex_label else name

    def create_control_widget(self, on_change_callback):
        self.min_val_selector = widgets.FloatText(value=self.min_val, layout=widgets.Layout(width="60px"))
        self.max_val_selector = widgets.FloatText(value=self.max_val, layout=widgets.Layout(width="60px"))
        self.slider = widgets.FloatSlider(
            value=self.value,
            min=self.min_val,
            max=self.max_val,
            step=self.step,
            description=self.latex_label,
            readout=True,
            continuous_update=True,
        )
        self.slider.observe(on_change_callback, names="value")
        self.min_val_selector.observe(self._val_range_changed, names="value")
        self.max_val_selector.observe(self._val_range_changed, names="value")

        return widgets.HBox([self.slider, self.min_val_selector, self.max_val_selector])

    def _val_range_changed(self, change):
        self.min_val = self.min_val_selector.value
        self.max_val = self.max_val_selector.value
        self.slider.min = self.min_val
        self.slider.max = self.max_val


class InteractivePlotter:

    FLOAT_TEXT_WIDTH = "150px"

    def __init__(self, plot_config: PlotConfig):
        self.config = plot_config

        self.latex_out = widgets.Output()
        if self.config.latex_str:
            with self.latex_out:
                display(Math(self.config.latex_str))

    def _setup_controls(self):
        control_widgets = []

        # Independent variable:
        self.independent_min = widgets.FloatText(
            value=self.config.independent_range[0], description="Min x:", layout=widgets.Layout(width=self.FLOAT_TEXT_WIDTH)
        )
        self.independent_max = widgets.FloatText(
            value=self.config.independent_range[1], description="Max x:", layout=widgets.Layout(width=self.FLOAT_TEXT_WIDTH)
        )
        self.independent_min.observe(self._update_plot, names="value")
        self.independent_max.observe(self._update_plot, names="value")

        control_widgets.append(widgets.HBox([self.independent_min, self.independent_max]))

        # Axis limits:
        self.xaxis_min = widgets.FloatText(
            value=self.config.independent_range[0], description="X-axis min:", layout=widgets.Layout(width=self.FLOAT_TEXT_WIDTH)
        )
        self.xaxis_max = widgets.FloatText(
            value=self.config.independent_range[1], description="X-axis max:", layout=widgets.Layout(width=self.FLOAT_TEXT_WIDTH)
        )
        self.xaxis_min.observe(self._update_plot, names="value")
        self.xaxis_max.observe(self._update_plot, names="value")

        control_widgets.append(widgets.HBox([self.xaxis_min, self.xaxis_max]))

        # Y-axis limits:
        self.yaxis_min = widgets.FloatText(value=0.0, description="Y-axis min:", layout=widgets.Layout(width=self.FLOAT_TEXT_WIDTH))
        self.yaxis_max = widgets.FloatText(value=1.0, description="Y-axis max:", layout=widgets.Layout(width=self.FLOAT_TEXT_WIDTH))
        self.yaxis_min.observe(self._update_plot, names="value")
        self.yaxis_max.observe(self._update_plot, names="value")
        control_widgets.append(widgets.HBox([self.yaxis_min, self.yaxis_max]))

        # Parameters:
        self.controls = {}
        for param, (min_val, max_val, step) in self.config.parameter_ranges.items():
            control = ParameterControl(
                name=param,
                value=self.config.parameters[param],
                min_val=min_val,
                max_val=max_val,
                step=step,
                latex_label=self.config.parameters_latex.get(param, None) if self.config.parameters_latex else None,
            )

            widget = control.create_control_widget(self._update_plot)
            slider = widget.children[0]
            self.controls[param] = slider
            control_widgets.append(widget)

        self.control_box = widgets.VBox(control_widgets)

    def display(self):
        self._setup_controls()
        self._make_plot()

        # Left side: LaTeX + controls.
        header_0 = widgets.HTML(value="<h2>Equation</h2>")
        header_1 = widgets.HTML(value="<h2>Controls</h2>")
        left_box = widgets.VBox(
            [header_0, self.latex_out, header_1, self.control_box],
            layout=widgets.Layout(
                align_items="center",  # center horizontally inside VBox
            ),
        )

        app = widgets.HBox([left_box, self.fig])  
        display(app)

    def _evaluate_function(self):
        params = {param: ctrl.value for param, ctrl in self.controls.items()}
        x_range = (self.independent_min.value, self.independent_max.value)
        x = np.linspace(x_range[0], x_range[1], 500)
        y = self.config.function(x, **params)
        return x, y

    def _make_plot(self):
        # Initialize figure
        self.fig = go.FigureWidget(layout=go.Layout(width=600, height=400))
        self.fig.update_layout(
            title=self.config.title,
            xaxis_title=self.config.xlabel,
            yaxis_title=self.config.ylabel,
            template="plotly_white",
            legend=dict(orientation="v", yanchor="bottom", y=0.9, xanchor="right", x=0.95),
            margin=dict(l=60, r=20, t=50, b=40),
        )

        # Calculate the function
        x, y = self._evaluate_function()
        main_trace = self.fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(width=4)))

    def _update_plot(self, *args, **kwargs):
        x, y = self._evaluate_function()
        self.fig.data[0].x = x
        self.fig.data[0].y = y

        self.fig.update_xaxes(range=[self.xaxis_min.value, self.xaxis_max.value])
        self.fig.update_yaxes(range=[self.yaxis_min.value, self.yaxis_max.value])
