from transshipment_lshaped_reduced import run_lshaped
from datetime import datetime, timedelta
import os
import csv

def load_coffee_house_data():
    # Get the directory of the current script
    current_dir = os.path.dirname(__file__)
    
    # Build the path to the data file relative to the repo root
    data_path = os.path.join(current_dir, "..", "..", "..", "data", "coffee_house_d08_200.csv")
    
    # Load and transform the data
    with open(data_path, newline="") as f:
        reader = csv.reader(f)
        a = [[float(x) * 9000 + 15000 for x in row] for row in reader]
    
    return a

a = load_coffee_house_data()
t_solve = timedelta(days=0, hours=0, minutes=5, seconds=0)
tc_saa = {} # dicitionary in style of {(s, nu): 'optimality gap'}
tc_saa_replication = {} # dicitionary in style of {(s, nu, num_replications): objective_value}

# TODO This just does one DOE
# REMOVE!!!
del a[1:]
sample_explore = 10

for scenario_doe in a:
    start_time = datetime.now()
    num_replication = 1
    number_samples_in_SAA = 10
    print(scenario_doe)
    objective_value, status, solution = run_lshaped(sample_explore, scenario_doe, 999999)
    # while True:
    #     elapsed = datetime.now() - start_time
    #     remaining = t_solve - elapsed
    #     # Solve
    #     print("Remaining", remaining.total_seconds())
    #     if remaining.total_seconds() > 0:  # Success
    #         # print(scenario_doe)
    #         objective_value, status, solution = run_lshaped(sample_explore, scenario_doe, solve_time_limit=remaining.total_seconds())
    #         # if status == "optimal":
    #         #     tc_saa_replication[(scenario_doe,number_samples_in_SAA,num_replication, status)] = objective_value
    #         #     num_replication += 1
    #         #     print(f"Remaining time: {remaining}; Replication {num_replication}; Result {objective_value}")

    #         # else:
    #         #     print("Ending with status: ", status)
    #     else:
    #         break
    

    # objective_value, status, solution = run_lshaped(sample_explore, scenario_doe, 999999)

print("ob", objective_value)
print("status", status)
print("solution", solution)