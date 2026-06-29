from .concentration_unit import concentration_unit
# from .concentration_mass_volume import concentration_mass_volume
from .molecular_weight import molecular_weight
from .reaction_equation import reaction_equation
from .reaction_data_analysis import reaction_data_analysis
from .buffer_equation import buffer_equation, buffer_visualization
from .data_uploader import DataUploader
from .sequence_properties import sequence_properties, sequence_dataframe
from .uvis_eyeballing import estimate_kd, visualize_simple_vs_quadratic
from .michaelis_menten import michaelis_menten_demo
from .solution_helper import SolutionHelper, solution_helper, concentration_mass_volume, mass_concentration_volume
from .dilution_helper import DilutionHelper, dilution_helper
from .michealis_menten_guesstimate import michealis_menten_guess

widgets = {
    "concentration_mass_volume": concentration_mass_volume,
    "concentration_unit": concentration_unit,
    "molecular_weight": molecular_weight,
    "buffer_equation": buffer_equation,
    "buffer_visualization": buffer_visualization,
    "reaction_equation": reaction_equation,
    "data_uploader": DataUploader,
    "reaction_data_analysis": reaction_data_analysis,
    "sequence_properties": sequence_properties,
    "sequence_dataframe": sequence_dataframe,
    "estimate_kd": estimate_kd,
    "visualize_simple_vs_quadratic": visualize_simple_vs_quadratic,
    "michaelis_menten_demo": michaelis_menten_demo,
    "solution_helper": solution_helper,
    "dilution_helper": dilution_helper,
    "michealis_menten_guess": michealis_menten_guess,
}

