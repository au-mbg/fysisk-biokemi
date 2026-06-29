import numpy as np
import pandas as pd

t = np.array([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
A_true, k_true = 10, 0.8
signal = A_true * np.exp(-k_true * t) + np.random.normal(0, 0.3, len(t))

pd = pd.DataFrame({
    'time': t,
    'signal': signal
})

pd.to_excel('exp_decay_data.xlsx', index=False)
