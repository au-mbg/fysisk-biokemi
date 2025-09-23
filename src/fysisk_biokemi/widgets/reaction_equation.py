import ipywidgets as widgets
from IPython.display import display, Math

prefix_to_factor = {
    "fM": 1e-15,
    "pM": 1e-12,
    "nM": 1e-9,
    "µM": 1e-6,
    "mM": 1e-3,
    "M": 1.0,
}


def chemical_formula_to_latex(formula):
    """Convert a chemical formula string to LaTeX format."""
    import re

    # Replace numbers with subscripted numbers
    def repl(match):
        return f"_{{{match.group(0)}}}"

    formula = re.sub(r"(\d+)", repl, formula)
    # Put chemical symbols in mathrm
    formula = re.sub(r"([A-Z][a-z]?)", r"\\mathrm{\1}", formula)

    # Handle parentheses
    formula = formula.replace("(", r"\left(").replace(")", r"\right)")
    return formula


def number_to_scientific_latex(num, precision=2):
    """Convert a number to scientific notation in LaTeX format."""
    if num == 0:
        return "0"
    exponent = int(f"{num:e}".split("e")[1])
    coefficient = num / (10**exponent)
    if exponent == 0:
        return f"{coefficient:.{precision}f}"
    else:
        return f"{coefficient:.{precision}f} \\times 10^{{{exponent}}}"


class ReactionTerm:
    def __init__(self, coefficient=1, formula="H2O", concentration=1.0, unit="M"):
        self.coefficient = coefficient
        self.formula = formula
        self.concentration = concentration
        self.raw_concentration = concentration  # Store the raw input value
        self.unit = unit

    def __repr__(self):
        return f"{self.coefficient} {self.formula} ({self.concentration} {self.unit})"

    def set_concentration(self, concentration, unit):
        """Set the concentration in Molar"""
        self.raw_concentration = concentration
        self.concentration = self.raw_concentration * prefix_to_factor[unit]
        self.unit = unit

    def on_change_unit(self, change):
        old_unit = change["old"]
        new_unit = change["new"]
        if old_unit != new_unit:
            concentration = self.raw_concentration
            self.set_concentration(concentration, new_unit)

    def on_change_concentration(self, change):
        new_conc = change["new"]
        self.set_concentration(new_conc, self.unit)


class Reaction:
    def __init__(self, reaction_string):
        self.reaction_string = reaction_string
        self.proper = self._parse_reaction()

    def _parse_reaction(self):
        # Split into reactants and products
        if "=" in self.reaction_string:
            reactants_str, products_str = self.reaction_string.split("=")
        elif "->" in self.reaction_string:
            reactants_str, products_str = self.reaction_string.split("->")
        else:
            return

        # Split into terms and parse coefficients and formulas
        reactants = reactants_str.split("+")
        products = products_str.split("+")

        for term in reactants + products:
            if not term.strip():
                return False

        reactants = [term.strip() for term in reactants]
        products = [term.strip() for term in products]

        # Find coefficients and formulas
        def parse_term(term):
            parts = term.split()
            if len(parts) == 2:
                coeff = int(parts[0])
                formula = parts[1]
            else:
                coeff = 1
                formula = parts[0]
            return coeff, formula

        reactants = [parse_term(term) for term in reactants]
        products = [parse_term(term) for term in products]

        self.reactants = [ReactionTerm(*r) for r in reactants]
        self.products = [ReactionTerm(*p) for p in products]

        return True

    def calculate_equilibrium_constant(self):
        try:
            K_eq = 1.0
            for term in self.products:
                K_eq *= term.concentration**term.coefficient
            for term in self.reactants:
                K_eq /= term.concentration**term.coefficient
            return K_eq
        except ZeroDivisionError:
            return None

    def get_equation_latex(self):
        def term_to_latex(term):
            coeff = term.coefficient
            formula = chemical_formula_to_latex(term.formula)
            if coeff == 1:
                return formula
            else:
                return f"{coeff} {formula}"

        reactants_latex = " + ".join(term_to_latex(t) for t in self.reactants)
        products_latex = " + ".join(term_to_latex(t) for t in self.products)
        return f"{reactants_latex} \\rightleftharpoons {products_latex}"

    def get_equilibrium_equation(self):
        numerator = ""
        denominator = ""


        def term_to_latex(term):
            coeff = term.coefficient
            formula = chemical_formula_to_latex(term.formula)
            if coeff == 1:
                return f"[{formula}]"
            else:
                return f"[{formula}]^{{{coeff}}}"

        # Equation string
        numerator = " \\cdot ".join(term_to_latex(t) for t in self.products)
        denominator = " \\cdot ".join(term_to_latex(t) for t in self.reactants)
        eq = f"K_{{eq}} = \\frac{{{numerator}}}{{{denominator}}}"

        # Equation with concentrations
        if all(t.concentration is not None for t in self.products + self.reactants):
            num_conc = " \\cdot ".join(
                f"({number_to_scientific_latex(t.concentration)})^{{{t.coefficient}}}" if t.coefficient > 1 else f"{number_to_scientific_latex(t.concentration)}" for t in self.products
            )
            denom_conc = " \\cdot ".join(
                f"({number_to_scientific_latex(t.concentration)})^{{{t.coefficient}}}" if t.coefficient > 1 else f"{number_to_scientific_latex(t.concentration)}" for t in self.reactants
            )
            eq += f" = \\frac{{{num_conc}}}{{{denom_conc}}}"

        # Result value
        value = self.calculate_equilibrium_constant()
        if value is not None:
            eq += f" = {number_to_scientific_latex(value)}"

        return eq


def add_term_input(term: ReactionTerm):
    conc_input = widgets.FloatText(
        description=f"[{term.formula}]:", value=term.concentration, style={"description_width": "initial"}
    )
    unit_input = widgets.Dropdown(
        options=prefix_to_factor.keys(), value=term.unit, description="Enhed:", style={"description_width": "initial"}
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
