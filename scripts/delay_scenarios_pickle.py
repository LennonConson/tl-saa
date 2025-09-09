import numpy as np
import pickle
import pprint
from scenario_creator_rail_reduced import generate_rail_travel_times
from scenario_creator_ship_reduced import generate_ship_travel_times
# np.random.seed(42)

# Function to generate random delays for ports
def generate_percentile_delays(set_J):
    return {entry: np.random.rand() for entry in set_J}
num_I = 5
num_J = 6
set_J = range(num_I + 1, num_I + num_J + 1)
outload_keys = [29]
num_V = 3
number_of_samples = [2,3,4,5,6,7,8,9,10] # all number of scenarios
num_replications = 6

average_delay=0.15
sigma=0.25
ship_sigma = 1.0

delay_dict = {}
for outload in outload_keys:
    for replication in range(num_replications):
        for n_samples in number_of_samples:
            scenario_dict = {}
            for i in range(n_samples):
                scenario_name = f"delay_scen{i}"
                delays = generate_percentile_delays(set_J)
                travel_time_by_rail  =  generate_rail_travel_times(divisions_per_day=3, percentile_delays=delays, average_delay=average_delay, sigma=sigma)
                ship_travel_times = generate_ship_travel_times(divisions_per_day=3, percentile_delays=delays, average_delay=average_delay, sigma=ship_sigma, num_V=num_V)
                scenario_dict[scenario_name, "delays"] = delays
                scenario_dict[scenario_name, "rail_travel_times"] = travel_time_by_rail
                scenario_dict[scenario_name, "ship_travel_times"] = ship_travel_times
            delay_dict[(outload, replication, n_samples)] = scenario_dict

with open(f"/home/user/git/tl-saa/data/delaydict_i{num_I}_j{num_J}_samples{num_replications}_outload29.txt", "w") as txtfile:
    pprint.pprint(delay_dict, stream=txtfile)
filename = f"/home/user/git/tl-saa/data/delaydict_i{num_I}_j{num_J}_samples{num_replications}_outload29.pkl"
with open(filename, "wb") as f:
    pickle.dump(delay_dict, f)


