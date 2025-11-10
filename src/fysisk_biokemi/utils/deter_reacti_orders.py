from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

def plot_dataframe(ax, df):
    # Extract from dataframe
    t = df['Time_s']
    A1 = df['A1_M']
    A2 = df['A2_M']

    # First subfigure: t vs [A]
    ax.plot(t, A1, 'o', label='[A1]')
    ax.plot(t, A2, 'o', label='[A2]')

    # EXTRA: Sets xlabel and shows legends.
    ax.set_xlabel('t [s]')
    ax.legend()

def make_fit(x_data, y_data, x_eval, A0, rate_laws, order):
    # Don't worry about this line for now. 
    # It just picks the correct function for the given order and sets A0.
    func = lambda t, k: rate_laws[order](t, k, A0)

    # Make fit
    popt, pcov = curve_fit(func, x_data, y_data)

    # Evaluate fit
    k = popt[0]
    y_fit = func(x_eval, k)
    return k, y_fit

def make_plot(df, rate_laws):
    # Extract data
    t = df['Time_s']
    A1 = df['A1_M']
    A2 = df['A2_M']
    orders = [0, 1, 2]
    t_eval = np.linspace(0, t.max()*1.1)
    A1_0 = A1.iloc[0] # Set the initial concentration [A1]_0
    A2_0 = A2.iloc[0] # Set the initial concentration [A2]_0


    fig, axes = plt.subplots(1, 3, figsize=(8, 4), sharey=True, layout='constrained')

    axes[0].set_ylabel('Concentration (M)')

    for ax in axes:
        plot_dataframe(ax, df)

    for ax, order in zip(axes, orders):
        k1, y_fit = make_fit(t, A1, t_eval, A1_0, rate_laws, order)
        ax.plot(t_eval, y_fit, color='C2', label=rf'k = {k1:.2e}')

        k2, y_fit = make_fit(t, A2, t_eval, A2_0, rate_laws, order)
        ax.plot(t_eval, y_fit, color='C3', label=rf'k = {k2:.2e}')
        ax.legend()
        ax.set_title(f'Reaction order: {order}')

