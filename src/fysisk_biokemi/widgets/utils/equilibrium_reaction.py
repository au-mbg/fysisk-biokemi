from fysisk_biokemi.widgets.utils.misc import (
    molar_prefix_to_factor,
    chemical_formula_to_latex,
    number_to_scientific_latex,
)

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
        self.concentration = self.raw_concentration * molar_prefix_to_factor[unit]
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

    def get_equilibrium_equation(self, with_values=True):
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
        if with_values:
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
    
    def get_reaction_orders(self):
        """Get the reaction orders based on the coefficients of the reactants."""
        orders = []
        for term in self.reactants:
            orders.append(term.coefficient)
        for term in self.products:
            orders.append(-term.coefficient)
        return orders
    
    def get_terms(self):
        term_formulas = [term.formula for term in self.reactants + self.products]
        return term_formulas
    
    def get_reaction_dicts(self):
        reactant_dict = {term.formula: term.coefficient for term in self.reactants}
        product_dict = {term.formula: term.coefficient for term in self.products}
        return reactant_dict, product_dict
