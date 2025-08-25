# Load outload data
from scipy.stats.qmc import Sobol
import pickle
import numpy as np
def generate_centered_sobol_samples(dim, n_samples, seed):
    sobol = Sobol(d=dim, scramble=False, seed=seed)
    samples = sobol.random(n=n_samples)
    return samples
dim = 5
n_samples = 100
seed = 42
all_outload = generate_centered_sobol_samples(dim, n_samples, seed)
np.set_printoptions(precision=4, suppress=True)
np.savetxt(f"/home/user/git/tl-saa/data/outload_{dim}_samples{n_samples}.txt", all_outload, fmt="%.4f")
filename = f"/home/user/git/tl-saa/data/outload_{dim}_samples{n_samples}.pkl"
with open(filename, "wb") as f:
    pickle.dump(all_outload, f)