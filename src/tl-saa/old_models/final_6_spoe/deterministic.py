import final_6_spoe
import pyomo.environ as pyo
import time
import csv

scenario_creator = final_6_spoe.scenario_creator
scenario_creator_kwargs = {
    "divisions_per_day": 3,
    "replication": 0
}

results = []

for scen_num in range(1, 100):  # scen1 to scen99
    scenario_name = f"scen{scen_num}"
    print(f"Using scenario: {scenario_name}")
    model = scenario_creator(scenario_name, **scenario_creator_kwargs)

    solver = pyo.SolverFactory('gurobi')
    start_time = time.time()
    result = solver.solve(model, tee=False)
    wall_time = time.time() - start_time

    y_open_values = {i: pyo.value(model.y_open[i]) for i in model.y_open}
    # Flatten results for CSV
    row = {'scenario': scenario_name, 'wall_time': wall_time}
    row.update({f'y_open[{i}]': v for i, v in y_open_values.items()})
    results.append(row)

# Write to CSV
fieldnames = ['scenario', 'wall_time'] + [f'y_open[{i}]' for i in model.y_open]
with open('deterministic_optimal_results.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow(row)