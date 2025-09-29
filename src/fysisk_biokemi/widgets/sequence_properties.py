import io
import ipywidgets as widgets
from IPython.display import display, Math
import numpy as np

from dataclasses import dataclass

@dataclass
class SequencePropertiesData:
    valid: bool = False
    sequence: str = ""
    molecular_weight: float = 0.0
    extinction_coefficient: float = 0.0
    isoelectric_point: float = 0.0
    charge_at_ph: float = 0.0

def calculate_properties(sequence: str, ph: float = 7.0) -> SequencePropertiesData:
    from Bio.SeqUtils.ProtParam import ProteinAnalysis
    try:
        analysis = ProteinAnalysis(sequence)
        mw = analysis.molecular_weight()
        ec = analysis.molar_extinction_coefficient()
        pi = analysis.isoelectric_point()
        return SequencePropertiesData(
            valid=True,
            sequence=sequence,
            molecular_weight=mw,
            extinction_coefficient=ec[0],  # assuming reduced form
            isoelectric_point=pi,
            charge_at_ph=analysis.charge_at_pH(ph)
        )
    except Exception as e:
        return SequencePropertiesData(sequence=sequence)


def sequences_to_df(file: str = None, sequences: list[str] = None, ph: float = 7.0):
    import pandas as pd
    from Bio.SeqIO.FastaIO import SimpleFastaParser

    if file is None and sequences is None:
        raise ValueError("Either file or sequences must be provided.")
    
    if sequences is None and file is not None:
        sequences = []
        with open(file) as handle:
            for _, seq in SimpleFastaParser(handle):
                sequences.append(seq)
    mw = []
    ec = []
    pi = []
    charge = []
    for seq in sequences:
        prop = calculate_properties(seq, ph)
        if prop.valid:
            mw.append(prop.molecular_weight)
            ec.append(prop.extinction_coefficient)
            pi.append(prop.isoelectric_point)
            charge.append(prop.charge_at_ph)

    data = {
        "Sequence": sequences,
        "Molecular Weight": mw,
        "Extinction Coefficient": ec,
        "Isoelectric Point": pi,
        "Charge": charge,
    }
    return pd.DataFrame(data)

class SequenceProperties:

    def __init__(self):
        self.sequence_input = widgets.Textarea(
            description="Aminosyresekvens:",
            layout=widgets.Layout(width="70%", height="100px"),
            style={"description_width": "initial"},
            placeholder="Sequence... (e.g., ACDEFGHIKLMNPQRSTVWY)",
        )

        self.ph_slider = widgets.FloatSlider(
            value=7.0,
            min=0.0,
            max=14.0,
            step=0.1,
            description="pH:",
            continuous_update=False,
            style={"description_width": "initial"},
        )

        self.sequence_input.observe(self._on_change, names="value")
        self.ph_slider.observe(self._on_change, names="value")
        self.output_area = widgets.Output()

    def display(self):
        input_box = widgets.VBox([self.sequence_input, self.ph_slider, self.output_area])
        display(input_box)

    def _on_change(self, change):
        seq = self.sequence_input.value
        ph = self.ph_slider.value
        prop = calculate_properties(seq, ph)

        if prop.valid:
            with self.output_area:
                self.output_area.clear_output()
                # Display header
                display(widgets.HTML("<h3>Protein Properties</h3>"))

                display(widgets.HTML(f"<font size='3'>Molecular weight: {prop.molecular_weight:.2f} g/mol</font>"))
                display(widgets.HTML(f"<font size='3'>Extinction coefficient: {prop.extinction_coefficient:.2f} M⁻¹cm⁻¹</font>"))
                display(widgets.HTML(f"<font size='3'>Isoelectric point: {prop.isoelectric_point:.2f}</font>"))
                display(widgets.HTML(f"<font size='3'>Charge at pH {ph:.1f}: {prop.charge_at_ph:.2f}</font>"))
        else:
            with self.output_area:
                self.output_area.clear_output()
                display(widgets.HTML("<h3>Protein Properties</h3>"))    
                display(widgets.HTML("<p>Please enter a valid amino acid sequence.</p>"))

class FastaToDataFrame:

    def __init__(self):
        self.uploader = widgets.FileUpload(
            accept=".fasta")
        self.ph_slider = widgets.FloatSlider(
            value=7.0,
            min=0.0,
            max=14.0,
            step=0.1,
            description="pH:", 
            continuous_update=False,
            style={"description_width": "initial"}
        )
        self.output_area = widgets.Output()

        self.uploader.observe(self._on_upload, names="value")
        self.ph_slider.observe(self._on_change, names="value")

    def display(self):
        input_box = widgets.VBox([self.uploader, self.ph_slider, self.output_area])
        display(input_box)

    def _on_upload(self, change):
        from Bio.SeqIO.FastaIO import SimpleFastaParser

        sequences = []
        raw_content = next(iter(self.uploader.value.values()))['content']
        raw_content = io.StringIO(raw_content.decode('utf-8'))

        for _, seq in SimpleFastaParser(raw_content):
            sequences.append(seq)

        self.sequences = sequences
        self._on_change(None)

    def _on_change(self, change):
        import dtale 
        if not hasattr(self, 'sequences'):
            return
        
        df = self.get_dataframe()

        with self.output_area:
            self.output_area.clear_output()
            d = dtale.show(df, ignore_duplicate=True)
            display(d)

    def get_dataframe(self):
        if hasattr(self, 'sequences'):
            ph = self.ph_slider.value
            return sequences_to_df(sequences=self.sequences, ph=ph)
        else:
            raise ValueError("No sequences have been uploaded yet.")


def sequence_properties():
    widget = SequenceProperties()
    widget.display()

def sequence_dataframe():
    widget = FastaToDataFrame()
    widget.display()
    return widget