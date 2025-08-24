import military_transshipment_port_selection as mtps
import pyomo.environ as pyo
import time

scenario_creator = mtps.scenario_creator
scenario_creator_kwargs = {
    "divisions_per_day": 3,
    "replication": 0
}

results = []
scen_num = 0
scenario_name = f"scen{scen_num}"
print(f"Using scenario: {scenario_name}")
model = scenario_creator(scenario_name, **scenario_creator_kwargs)
solver = pyo.SolverFactory('gurobi')
start_time = time.time()
result = solver.solve(model, tee=True)
wall_time = time.time() - start_time
print(f"Solved in {wall_time:.2f} seconds")
