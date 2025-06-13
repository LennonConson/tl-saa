from transshipment_lshaped import run_lshaped
from datetime import datetime, timedelta
import os
import csv

def load_coffee_house_data():
    # Get the directory of the current script
    current_dir = os.path.dirname(__file__)
    
    # Build the path to the data file relative to the repo root
    data_path = os.path.join(current_dir, "..", "..", "data", "coffee_house_d20_200.csv")
    
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
sample_explore = 2

for scenario_doe in a:
    objective_value, status, solution = run_lshaped(sample_explore, scenario_doe, 999999)

print(objective_value)
print(status)