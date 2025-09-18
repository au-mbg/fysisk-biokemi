import numpy as np


def make_dataset(
    k_forward: float,
    k_backward: float,
    A0: float = 1,
    B0: float = 0,
    n_samples: int = 200,
    t0: float = 0,
    t1: float = 10,
    noise_level: float = 0.05,
):
    t = np.linspace(t0, t1, n_samples)
    A_t = A0 / (k_forward + k_backward) * (k_backward + k_forward * np.exp(-(k_forward + k_backward) * t))
    B_t = (A0 - A_t) + B0
    return t, A_t, B_t

def make_dataframe(dataset):
    import pandas as pd

    t, A, B = dataset
    df = pd.DataFrame({"time": t, "A": A, "B": B})
    return df


if __name__ == "__main__":
    k_forward = 1.0
    k_backward = 0.5

    dataset = make_dataset(k_forward, k_backward)
    df = make_dataframe(dataset)
    df.to_csv("reversible_reaction_dataset.csv", index=False, sep=' ')



