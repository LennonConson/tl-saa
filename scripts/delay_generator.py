import numpy as np
import pickle

num_scen = 100
replications = 100
all_scenario_names = [f"scen{sn}" for sn in range(num_scen)]
num_I = 6
num_J = 6
set_J = range(num_I + 1, num_I + num_J + 1)

def generate_percentile_delays():
    return {entry: np.random.rand() for entry in set_J}

scenario_replication_percentile_delays = {
    (name, rep): generate_percentile_delays()
    for name in all_scenario_names
    for rep in range(replications)
}
with open("scenario_replication_percentile_delays_i10_j6.pkl", "wb") as f:
    pickle.dump(scenario_replication_percentile_delays, f)
