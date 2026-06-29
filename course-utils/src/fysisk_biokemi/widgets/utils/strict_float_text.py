import re
import traitlets as tl
import ipywidgets as widgets

import numpy as np

_FLOAT_RE = re.compile(
    r"""^\s*                              # leading space
         [+-]?                            # optional sign
         (?:                              # mantissa
             (?:\d+(?:\.\d*)?)            # 123 or 123. or 123.45
             | (?:\.\d+)                  # .45
         )
         (?:[eE][+-]?\d+)?                # optional exponent
         \s*$                              # trailing space
    """,
    re.VERBOSE,
)

class StrictFloatText(widgets.VBox):
    """
    A float input built from widgets.Text that *disallows commas* and shows
    an inline error. Exposes a validated float via `.value` and the raw text via `.text`.

    Parameters (subset mirrors widgets.Text):
        description: str = ""
        placeholder: str = "Use '.' for decimals (e.g. 1.43)"
        disabled: bool = False
        layout: widgets.Layout = None
        style: widgets.WidgetStyle = None
        continuous_update: bool = True   # validate as the user types
        required: bool = False           # if True, empty input is an error
        show_error: bool = True          # show HTML error line
        strict_dot: bool = True          # if True, any ',' triggers an error

    Public attributes:
        value: Optional[float]  (validated; None if empty/invalid)
        text: str               (raw text in the Text box)
        error_html: widgets.HTML

    Events:
        .observe(handler, names="value")  # fires when validated value changes
        .observe(handler, names="text")   # fires on raw text changes
        .observe(handler, names="error")  # fires when error message changes
    """

    # Expose traits so users can observe them like normal widgets
    value = tl.Any(allow_none=True)       # validated float or None
    text = tl.Unicode("")                 # raw text as typed
    error = tl.Unicode("", help="Error message (empty if OK)")

    def __init__(
        self,
        description: str = "",
        placeholder: str = "Use '.' for decimals (e.g. 1.43)",
        disabled: bool = False,
        layout: widgets.Layout | None = None,
        style: dict | None = None,
        continuous_update: bool = True,
        required: bool = False,
        show_error: bool = True,
        strict_dot: bool = True,
        **text_kwargs,
    ):
        self._strict_dot = bool(strict_dot)
        self._required = bool(required)
        self._continuous_update = bool(continuous_update)
        self._suppress_value_events = False

        # Inner widgets
        self.text_input = widgets.Text(
            description=description,
            placeholder=placeholder,
            disabled=disabled,
            layout=layout or widgets.Layout(),
            style=style if isinstance(style, dict) else (style or {}),
            **text_kwargs,
        )
        # encourage numeric keyboard on touch devices
        try:
            self.text_input.add_class("inputmode-decimal")
        except Exception:
            pass

        self.error_html = widgets.HTML(layout=widgets.Layout(margin="0 0 0.25rem 0"))
        if not show_error:
            self.error_html.layout.display = "none"

        # Initialize the VBox
        super().__init__(children=[self.text_input, self.error_html])

        # Wire events
        self.text_input.observe(self._on_text_change, names="value")
        # Validate immediately on blur (Enter/tab) to catch final state
        self.text_input.on_submit(self._on_submit)

        # Initial sync of public traits
        self.set_error("")  # clears error_html
        self.set_trait("text", self.text_input.value)
        self._validate_and_update(self.text_input.value, fire_change=False)

    # ---------- Public helpers ----------
    def set_error(self, msg: str):
        """Set error message (also updates error_html)."""
        self.set_trait("error", msg)
        if msg:
            self.error_html.value = f"<span style='color:#b00020;'>{msg}</span>"
        else:
            self.error_html.value = ""

    # ---------- Event handlers ----------
    def _on_text_change(self, change):
        new_text = change["new"] or ""
        # Mirror raw text trait
        self.set_trait("text", new_text)

        if self._continuous_update:
            self._validate_and_update(new_text, fire_change=True)
        else:
            # Only enforce comma warning in non-continuous mode
            if self._strict_dot and "," in new_text:
                self.set_error("Brug punktum (.) som decimalseparator — ikke komma (,).")
            else:
                self.set_error("")

    def _on_submit(self, _):
        self._validate_and_update(self.text_input.value or "", fire_change=True)

    # ---------- Core validation ----------
    def _validate_and_update(self, txt: str, fire_change: bool):
        txt_stripped = txt.strip()

        error_value = np.nan

        # Empty handling
        if txt_stripped == "":
            if self._required:
                self._assign_value(error_value, fire_change, error="Feltet må ikke være tomt.")
            else:
                self._assign_value(error_value, fire_change, error="")
            return

        # Comma rule
        if self._strict_dot and "," in txt_stripped:
            self._assign_value(
                error_value,
                fire_change,
                error="Brug punktum (.) som decimalseparator — ikke komma (,).",
            )
            return

        # Numeric format (dot as decimal, optional exponent)
        if not _FLOAT_RE.match(txt_stripped):
            self._assign_value(
                error_value,
                fire_change,
                error="Ugyldigt talformat. Brug f.eks. 1.43 eller -2.0e-3.",
            )
            return

        # Safe float conversion
        try:
            new_val = float(txt_stripped)
        except Exception:
            self._assign_value(error_value, fire_change, error="Kunne ikke fortolke tallet.")
            return

        # Success
        self._assign_value(new_val, fire_change, error="")

    def _assign_value(self, new_val, fire_change: bool, error: str):
        prev_val = getattr(self, "value", None)
        self.set_error(error)

        # Only set & notify if changed (including None↔number transitions)
        changed = (repr(prev_val) != repr(new_val))
        if changed:
            # Avoid re-entrant loops if users set .value in handlers
            self._suppress_value_events = True
            try:
                self.set_trait("value", new_val)
            finally:
                self._suppress_value_events = False

        # In ipywidgets, setting the trait will itself trigger observers.
        # We respect fire_change; if not firing, we can briefly block handlers.
        if not fire_change and changed:
            # Roll back notification by resetting to same value (no-op for observers)
            self.set_trait("value", new_val)

    # ---------- Convenience API (optional, FloatText-like) ----------
    @property
    def description(self):
        return self.text_input.description

    @description.setter
    def description(self, v):
        self.text_input.description = v

    @property
    def disabled(self):
        return self.text_input.disabled

    @disabled.setter
    def disabled(self, v):
        self.text_input.disabled = v

    @property
    def placeholder(self):
        return self.text_input.placeholder

    @placeholder.setter
    def placeholder(self, v):
        self.text_input.placeholder = v