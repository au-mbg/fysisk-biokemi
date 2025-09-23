import ipywidgets as widgets
from IPython.display import display, Math

# --- unit factors ---
MASS_FACTORS = {
    "g": 1.0,
    "mg": 1e-3,
    "µg": 1e-6,  # unicode micro
    "ng": 1e-9,
}

VOLUME_FACTORS = {
    "L": 1.0,
    "mL": 1e-3,
    "µL": 1e-6,
}

def molarity_from_mass_volume(mass_value, mass_unit, volume_value, volume_unit, mw_g_per_mol):
    mass_g = mass_value * MASS_FACTORS[mass_unit]
    volume_L = volume_value * VOLUME_FACTORS[volume_unit]
    if mw_g_per_mol <= 0 or volume_L <= 0:
        return float('nan')
    moles = mass_g / mw_g_per_mol
    return moles / volume_L  # M

def concentration_mass_volume():

    mass_value = widgets.FloatText(description="Masse:", value=70.0)
    mass_unit  = widgets.Dropdown(description="Enhed:", options=["µg","ng","mg","g"], value="µg")

    volume_value = widgets.FloatText(description="Volumen:", value=1.0)
    volume_unit  = widgets.Dropdown(description="Enhed:", options=["mL","µL","L"], value="mL")

    mw_value = widgets.FloatText(description="Mol.vægt (g/mol):", value=190000.0, style={'description_width': 'initial'})

    out = widgets.Output()

    def update(*args):
        M = molarity_from_mass_volume(
            mass_value.value, mass_unit.value,
            volume_value.value, volume_unit.value,
            mw_value.value
        )
        with out:
            out.clear_output()
            if M != M:  # NaN
                display(Math(r"\text{Fejl: Tjek at MW og volumen er > 0}"))
            else:
                base = f"{M:e}"[0:5]
                exponent = int(f"{M:e}".split("e")[1])
                latex_str = (
                    r"\text{Koncentration: }"
                    + rf"{base} \times 10^{{{exponent}}} \,\mathrm{{M}}"
                )
                display(Math(latex_str))

    for w in (mass_value, mass_unit, volume_value, volume_unit, mw_value):
        w.observe(update, names="value")

    update()

    ui = widgets.VBox([
        widgets.HBox([mass_value, mass_unit]),
        widgets.HBox([volume_value, volume_unit]),
        mw_value,
        out
    ])

    display(ui)
