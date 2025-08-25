import military_transshipment_port_selection as mtps
import pickle
import pyomo.environ as pyo
import time
from mpisppy.opt.lshaped import LShapedMethod
# Scenarioes generatation
replications = 0
num_samples = 2
outload_key = 0
print(f"Generating {num_samples} samples for replication {replications}.")

with open("/home/user/git/tl-saa/data/outload_5_samples100.pkl", "rb") as f:
    all_outload = pickle.load(f)
outload= all_outload[outload_key]
print(f"Using outload key {outload_key}.")
print(f"Outload: {outload}")
all_scenario_names = [f"delay_scen{i}" for i in range(num_samples)]
print(f"Scenario names: {all_scenario_names}")

replication = 0

# Deterministic model creation and solving
scenario_creator = mtps.scenario_creator
scenario_creator_kwargs = {
    "divisions_per_day": 3,
    "outload": outload,
    "replication": replication,
    "max_days": 20
}
scenario_name = all_scenario_names[0]  # Just pick the first scenario for this example

# model = scenario_creator(scenario_name, **scenario_creator_kwargs)
# solver = pyo.SolverFactory('gurobi')
# start_time = time.time()
# result = solver.solve(model, tee=True)
# wall_time = time.time() - start_time
# print(f"Solved in {wall_time:.2f} seconds")

bounds = {name: -432000 for name in all_scenario_names}
options = {
    "root_solver": "gurobi_persistent",
    "sp_solver": "gurobi_persistent",
    "sp_solver_options" : {"threads" : 10},
    "valid_eta_lb": bounds,
    "max_iter": 100,
}
ls = LShapedMethod(options, all_scenario_names, scenario_creator, 
                   scenario_creator_kwargs=scenario_creator_kwargs)
result = ls.lshaped_algorithm()