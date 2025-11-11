from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

def make_fits_and_plots(df, n_points):

    def linear_func(x, a, b):
        return a * x + b

    # Variables to store calculated values.
    slopes = []
    concentrations = []
    substrate_concentrations = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    fig, axes = plt.subplots(3, 3, figsize=(8, 8), sharex=True, sharey='row') # We make the figure while also finding the slopes.
    for i, (s, ax) in enumerate(zip(substrate_concentrations, axes.flatten())): # Don't worry about the details of this.

        # Make the
        conc_col_name = f'C_S{s}'
        x_data = df['time_(s)'][:n_points]
        y_data = df[conc_col_name][:n_points]
        popt, pcov = curve_fit(linear_func, x_data, y_data)

        # Plot the data
        ax.plot(df['time_(s)'], df[conc_col_name], 'o', color=f'C{i}', label=f'[S]={s} uM')

        # Plot the fit
        t_smooth = np.linspace(0, 10, 10)
        ax.plot(t_smooth, linear_func(t_smooth, *popt), color='black', linestyle='-')

        # Customize
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Concentration (M)')
        ax.legend()

        # Store calculated slopes and concentrations, concentration converted to molar.
        slopes.append(popt[0])
        concentrations.append(s * 10**(-6))

    return slopes, concentrations