import numpy as np
import pprint
import pickle
# Function to generate random delays for ports
def generate_percentile_delays(set_J):
    return {entry: np.random.rand() for entry in set_J}
num_I = 5
num_J = 6
set_J = range(num_I + 1, num_I + num_J + 1)


number_of_samples = [300] # all number of scenarios
num_replications = 4

delay_dict = {}

for replication in range(num_replications):
    for n_samples in number_of_samples:
        scenario_dict = {}
        for i in range(n_samples):
            scenario_name = f"delay_scen{i}"
            delays = generate_percentile_delays(set_J)
            scenario_dict[scenario_name] = delays
        delay_dict[(replication, n_samples)] = scenario_dict

with open(f"/home/user/git/tl-saa/data/delaydict_i{num_I}_j{num_J}_samples{num_replications}.txt", "w") as txtfile:
    pprint.pprint(delay_dict, stream=txtfile)
filename = f"/home/user/git/tl-saa/data/delaydict_i{num_I}_j{num_J}_samples{num_replications}_outload36_300.pkl"
with open(filename, "wb") as f:
    pickle.dump(delay_dict, f)
# (replication, number_of_samples): (scenario_name, delays)

