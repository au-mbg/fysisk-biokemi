
molar_prefix_to_factor = {
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

