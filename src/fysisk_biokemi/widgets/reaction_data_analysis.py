# ReactionKeqWidget: upload CSV, map columns/units, parse reaction,
# convert concentrations to M, compute Keq(t), show LaTeX and plot.

import io
import re
import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, Math
import matplotlib.pyplot as plt

from fysisk_biokemi.widgets.utils import Reaction


class ReactionKeqWidget:
    """Interactive tool for K_eq time-series from CSV data.

    Expected CSV: one time column + any number of species columns.
    Column headers may include units in parentheses, e.g. 'A (nM)'.
    Reaction syntax: '2 A + B = X + 3 Y'
    """

    UNIT_MAP = {
        "fM": 1e-15,
        "pM": 1e-12,
        "nM": 1e-9,
        "µM": 1e-6,  # unicode micro
        "uM": 1e-6,  # ASCII fallback
        "mM": 1e-3,
        "M": 1.0,
    }
    TIME_MAP = {"s": 1.0, "min": 60.0, "h": 3600.0}
    UNIT_OPTIONS = ["fM", "pM", "nM", "µM", "uM", "mM", "M"]

    HEADER_UNIT_REGEX = re.compile(r"^(.*?)[\(\[\{]\s*([fpnµu]M|mM|M)\s*[\)\]\}]\s*$")

    # -------------------- Construction --------------------
    def __init__(self, default_reaction="A + B = X + Y"):
        # state
        self._df = None  # original DataFrame
        self._species_rows = []  # rows in mapping box

        # widgets (left pane)
        self.header_html = widgets.HTML("<h3>Data & reaktion</h3>")
        self.uploader = widgets.FileUpload(accept=".csv", multiple=False, description="Upload CSV")
        self.reaction_text = widgets.Text(
            value=default_reaction, description="Reaktion:", placeholder="fx '2 A + B = X'"
        )
        self.time_col_dd = widgets.Dropdown(description="Tid kolonne:")
        self.time_unit_dd = widgets.Dropdown(description="Tid enhed:", options=list(self.TIME_MAP.keys()), value="s")

        # widgets (right pane)
        self.species_map_box = widgets.VBox([])
        self.process_btn = widgets.Button(description="Beregn og plot", button_style="primary")
        self.status_out = widgets.Output(layout={"border": "1px solid #ddd"})
        self.latex_out = widgets.Output()
        self.plot_out = widgets.Output()
        self.table_out = widgets.Output()

        # layout
        self.left = widgets.VBox(
            [
                self.header_html,
                widgets.HBox([self.uploader, self.process_btn]),
                self.reaction_text,
                self.time_col_dd,
                self.time_unit_dd,
            ]
        )
        self.right = widgets.VBox(
            [
                self.species_map_box,
                self.status_out,
            ]
        )

        self.bottom = widgets.HBox(
            [
                self.plot_out,
                widgets.VBox([widgets.HTML("<h3>Reaktionsligning</h3>"), self.latex_out]),
            ]
        )

        # events
        self.uploader.observe(self._on_upload_change, names="value")
        self.reaction_text.observe(self._on_reaction_change, names="value")
        self.process_btn.on_click(self._process)

    # -------------------- Public API --------------------
    def display(self):
        """Render the full UI."""
        full_widget = widgets.VBox(
            [
                widgets.HBox([self.left, self.right]),
                self.bottom,
            ]
        )
        display(full_widget)

    # -------------------- Parsing helpers --------------------
    @staticmethod
    def _unit_from_header(name):
        """
        Detect a unit in headers like 'A (nM)', 'B[µM]', 'X{mM}'.
        Returns (base_label, unit_or_None).
        """
        m = ReactionKeqWidget.HEADER_UNIT_REGEX.search(name)
        if m:
            base = m.group(1).strip()
            unit = m.group(2)
            if unit == "uM":
                unit = "µM"
            return base, unit
        return name.strip(), None

    @staticmethod
    def _parse_reaction(text):
        """
        Parse '2 A + B = X + 3 Y' -> (reactants dict, products dict)
        e.g. ({'A': 2, 'B': 1}, {'X': 1, 'Y': 3})
        """
        reaction = Reaction(text)
        return reaction

    # -------------------- UI building --------------------
    def _build_species_mapping_ui(self, species_names, df_columns):
        """
        For each species, create a row with:
          - Dropdown to choose which CSV column maps to the species
          - Unit dropdown (prefilled from header if present)
        """
        rows = [widgets.HTML("<h3>Kolonnetilknytning (vælg kolonne og enhed for hver art)</h3>")]
        self._species_rows = []

        for s in species_names:
            # Attempt to auto-match by base label
            default_col = None
            default_unit = "M"
            for col in df_columns:
                base, unit = self._unit_from_header(col)
                if base == s and default_col is None:
                    default_col = col
                    if unit:
                        default_unit = "µM" if unit == "uM" else unit

            col_dd = widgets.Dropdown(
                options=list(df_columns),
                value=default_col if default_col in df_columns else None,
                description=f"{s} kol.:",
            )

            # Guess unit from header of chosen column
            unit_guess = None
            if col_dd.value:
                _, u = self._unit_from_header(col_dd.value)
                unit_guess = "µM" if u == "uM" else u
            unit_dd = widgets.Dropdown(
                options=self.UNIT_OPTIONS, value=unit_guess or default_unit, description="Enhed:"
            )

            row = widgets.HBox([col_dd, unit_dd])
            rows.append(row)
            self._species_rows.append((s, col_dd, unit_dd))

        self.species_map_box.children = rows

    def _on_upload_change(self, _):
        self._clear_outputs()
        if not self.uploader.value:
            return

        # Read CSV
        content = self.uploader.value[list(self.uploader.value.keys())[0]]['content']
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            with self.status_out:
                print(f"Kunne ikke læse CSV: {e}")
            return

        self._df = df
        cols = list(df.columns)

        # Time column guess: first column
        self.time_col_dd.options = cols
        self.time_col_dd.value = cols[0] if cols else None

        # Build species mapping from current reaction
        try:
            reaction = self._parse_reaction(self.reaction_text.value)
            species_order = reaction.get_terms()
            self._build_species_mapping_ui(species_order, cols)
            with self.status_out:
                print(f"Indlæst data: {df.shape[0]} rækker, {df.shape[1]} kolonner.")
        except Exception as e:
            self.species_map_box.children = []
            with self.status_out:
                print(f"Fejl ved parsing af reaktion: {e}")

    def _on_reaction_change(self, _):
        if self._df is None:
            return
        cols = list(self._df.columns)
        try:
            reaction = self._parse_reaction(self.reaction_text.value)
            species_order = reaction.get_terms()
            self._build_species_mapping_ui(species_order, cols)
        except Exception as e:
            self.species_map_box.children = [widgets.HTML(f"<b style='color:red'>Fejl: {e}</b>")]

    def _collect_mapping(self):
        """Return (time_col, time_unit, mapping dict {species: (col, unit)})."""
        mapping = {}
        for s, col_dd, unit_dd in self._species_rows:
            mapping[s] = (col_dd.value, unit_dd.value)
        return self.time_col_dd.value, self.time_unit_dd.value, mapping

    @staticmethod
    def _keq_series(reactants, products, df_M):
        """Compute Keq = Π products [S]^v / Π reactants [S]^v for each row."""
        num = pd.Series(1.0, index=df_M.index, dtype=float)
        den = pd.Series(1.0, index=df_M.index, dtype=float)
        for s, nu in products.items():
            num *= np.power(df_M[s], nu)
        for s, nu in reactants.items():
            den *= np.power(df_M[s], nu)
        with np.errstate(divide="ignore", invalid="ignore"):
            return num / den

    def _process(self, _):
        self._clear_outputs()
        if self._df is None:
            with self.status_out:
                print("Upload venligst en CSV først.")
            return

        # Parse reaction
        try:
            reaction = self._parse_reaction(self.reaction_text.value)
        except Exception as e:
            with self.status_out:
                print(f"Fejl i reaktionsligning: {e}")
            return

        # Collect mapping
        time_col, time_unit, mapping = self._collect_mapping()
        needed = reaction.get_terms()
        missing = [s for s in needed if mapping.get(s, (None, None))[0] is None]
        if missing:
            with self.status_out:
                print(f"Manglende kolonnetilknytning for: {', '.join(missing)}")
            return

        df = self._df.copy()

        # Time vector in seconds
        if time_col not in df.columns:
            with self.status_out:
                print(f"Tid kolonne '{time_col}' findes ikke.")
            return
        try:
            t_raw = pd.to_numeric(df[time_col], errors="coerce").to_numpy(dtype=float)
        except Exception:
            with self.status_out:
                print("Kunne ikke konvertere tidskolonnen til tal.")
            return
        t_s = t_raw * self.TIME_MAP.get(time_unit, 1.0)

        # Concentrations in M
        conc_M = {}
        for s, (col, unit) in mapping.items():
            if col not in df.columns:
                with self.status_out:
                    print(f"Valgt kolonne '{col}' findes ikke for {s}.")
                return
            values = pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=float)
            # normalize uM -> µM
            unit_norm = "µM" if unit == "uM" else unit
            factor = self.UNIT_MAP[unit_norm]
            conc_M[s] = values * factor

        df_M = pd.DataFrame(conc_M)
        reactants, products = reaction.get_reaction_dicts()
        keq = self._keq_series(reactants, products, df_M)

        # LaTeX expression
        with self.latex_out:
            eq = reaction.get_equation_latex()
            expr = reaction.get_equilibrium_equation(with_values=False)
            display(Math(eq))
            display(Math(expr))

        # Plot Keq vs time
        with self.plot_out:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(t_s, keq, color="mediumpurple")
            ax.set_xlabel("Tid (s)")
            ax.set_ylabel(r"$K_{eq}$")
            ax.grid(True, which="both", ls="--", lw=0.5)
            plt.tight_layout()
            plt.show()

        # Preview table (first 6 rows)
        with self.table_out:
            preview = pd.DataFrame({"time_s": t_s, **df_M, "Keq": keq}).head(6)
            display(preview)

        with self.status_out:
            print(
                "Færdig: koncentrationer konverteret til M, Keq beregnet og plottet.\n"
                f"Antal søjler i data: {self._df.shape[1]}"
            )

    # -------------------- Utilities --------------------
    def _clear_outputs(self):
        self.status_out.clear_output()
        self.latex_out.clear_output()
        self.plot_out.clear_output()
        self.table_out.clear_output()


def reaction_data_analysis(default_reaction="A + B = X + Y"):
    """Helper to quickly create and display the ReactionKeqWidget."""
    app = ReactionKeqWidget(default_reaction=default_reaction)
    app.display()
