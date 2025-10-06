import ipywidgets as widgets
from IPython.display import display, Math
from fysisk_biokemi.widgets.utils.equilibrium_reaction import Reaction, ReactionTerm
from fysisk_biokemi.widgets.utils.misc import molar_prefix_to_factor
from fysisk_biokemi.widgets.utils import StrictFloatText




def add_term_input(term: ReactionTerm):
    conc_input = StrictFloatText(
        description=f"[{term.formula}]:", value=f"{term.concentration}", style={"description_width": "initial"}
    )
    unit_input = widgets.Dropdown(
        options=molar_prefix_to_factor.keys(), value=term.unit, description="Enhed:", style={"description_width": "initial"}
    )
    box = widgets.HBox([conc_input, unit_input])
    return box, conc_input, unit_input


def reaction_equation():
    reaction_input = widgets.Text(
        description="Reaktion:", value="A + B = C", style={"description_width": "initial"}
    )

    inputs_box = widgets.VBox([])

    output = widgets.Output()
    output_label = widgets.Label("Resultat")
    outputs_box = widgets.VBox([output_label, output])

    def on_reaction_change(change):
        output.clear_output()

        reaction_str = change["new"]
        reaction = Reaction(reaction_str)
        if reaction.proper:
            # Clear previous inputs
            inputs_box.children = [widgets.Label("Reaktanter")]

            widgets_list = []

            # Add new inputs for reactants
            for r in reaction.reactants:
                box, conc_input, unit_input = add_term_input(r)
                inputs_box.children += (box,)
                conc_input.observe(r.on_change_concentration, names="value")
                unit_input.observe(r.on_change_unit, names="value")
                widgets_list += [conc_input, unit_input]

            # Add new inputs for products
            inputs_box.children += (widgets.Label("Produkter"),)
            for p in reaction.products:
                box, conc_input, unit_input = add_term_input(p)
                inputs_box.children += (box,)
                conc_input.observe(p.on_change_concentration, names="value")
                unit_input.observe(p.on_change_unit, names="value")
                widgets_list += [conc_input, unit_input]

            def update_equilibrium(*args):
                output.clear_output()
                with output:
                    display(Math(reaction.get_equation_latex()))
                    display(Math(reaction.get_equilibrium_equation()))

            for widget in widgets_list:
                widget.observe(update_equilibrium, names="value")

            update_equilibrium()

    on_reaction_change({"new": "A + B = C"})

    reaction_input.observe(on_reaction_change, names="value")
    widget = widgets.VBox([reaction_input, inputs_box, outputs_box])
    display(widget)


if __name__ == "__main__":
    Reaction("2 H2O + O2 =")
