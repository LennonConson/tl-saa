import final_6_spoe
import pyomo.environ as pyo
import sys

# Get scenario name from command line or use default
scenario_creator = final_6_spoe.scenario_creator
if len(sys.argv) > 1:
    scenario_name = sys.argv[1]
else:
    scenario_name = 'scen0'  # Default scenario

scenario_creator_kwargs = {
        "divisions_per_day": 3,
        "max_days": 16,
        "replication": 0
    }

print(f"Using scenario: {scenario_name}")
model = scenario_creator(scenario_name, **scenario_creator_kwargs)

solver = pyo.SolverFactory('gurobi')
result = solver.solve(model, tee=True)

print(result)
for i in model.y_open:
    print(f"y_open[{i}] = {pyo.value(model.y_open[i])}")