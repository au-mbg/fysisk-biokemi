import ipywidgets as widgets
from IPython.display import display

from fysisk_biokemi.widgets.utils import molar_prefix_to_factor
from fysisk_biokemi.widgets.utils import StrictFloatText


def concentration_unit():
    # Map SI prefix to power of ten
    prefix_to_factor = molar_prefix_to_factor

    def convert_to_M(value, unit):
        factor = prefix_to_factor[unit]
        return value * factor

    # Input widgets
    value_box = StrictFloatText(description="Værdi:", value="1.0")
    unit_box = widgets.Dropdown(
        description="Enhed:",
        options=list(prefix_to_factor.keys()),
        value="µM"
    )
    output_box = widgets.Label(value="Resultat: ", layout=widgets.Layout(width='200px'))
    output_box.style.font_weight = "bold"

    # Update function
    def update_result(*args):
        val = convert_to_M(value_box.value, unit_box.value)
        output_box.value = f"Resultat: {val:.3e} M"

    # Trigger update when input changes
    value_box.observe(update_result, names="value")
    unit_box.observe(update_result, names="value")

    # Initial calculation
    update_result()

    # Display widget
    widget = widgets.HBox([value_box, unit_box])
    widget = widgets.VBox([widget, output_box])
    display(widget)
