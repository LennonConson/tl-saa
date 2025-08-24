from scipy.stats.qmc import Sobol
import pickle

def generate_centered_sobol_samples(dim=5, n_samples=100, seed=None):
    sobol = Sobol(d=dim, scramble=False, seed=seed)
    samples = sobol.random(n=n_samples)
    return samples

if __name__ == "__main__":
    dim = 5
    n_samples = 100
    seed = 42  # For reproducibility
    samples = generate_centered_sobol_samples(dim, n_samples, seed=seed)


    scenarios = {f"scen{i}": sample.tolist() for i, sample in enumerate(samples)}
    filename = f"outload_i{dim}_samp{n_samples}.pkl"
    with open(filename, "wb") as f:
        pickle.dump(scenarios, f)