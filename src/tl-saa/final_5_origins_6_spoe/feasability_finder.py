import feasability_finder_military_transshipment_port_selection as mtps
import pyomo.environ as pyo
import time
import csv

scenario_creator = mtps.scenario_creator
divisions_per_day = 3
replication = 0

min_max_days = 13
max_max_days = 40  # Set an upper limit to avoid infinite loops

results = []

for scen_idx in range(100):
    scenario_name = f"scen{scen_idx}"
    found = False
    for max_days in range(min_max_days, max_max_days + 1):
        scenario_creator_kwargs = {
            "divisions_per_day": divisions_per_day,
            "replication": replication,
            "max_days": max_days
        }
        print(f"Trying {scenario_name} with max_days={max_days}")
        model = scenario_creator(scenario_name, **scenario_creator_kwargs)
        solver = pyo.SolverFactory('gurobi')
        solver.options['MIPGap'] = 0.99  # 1% gap for 99% solution
        start_time = time.time()
        result = solver.solve(model, tee=False)
        wall_time = time.time() - start_time

        if (result.solver.status == pyo.SolverStatus.ok and
            result.solver.termination_condition in [pyo.TerminationCondition.optimal, pyo.TerminationCondition.feasible]):
            print(f"99% solution found for {scenario_name} at max_days={max_days} in {wall_time:.2f} seconds")
            results.append({"scenario_name": scenario_name, "max_days": max_days})
            found = True
            break
        else:
            print(f"No 99% solution for {scenario_name} at max_days={max_days}")

    if not found:
        results.append({"scenario_name": scenario_name, "max_days": None})

# Save results to CSV
csv_path = "first_successful_max_days_by_scenario.csv"
with open(csv_path, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["scenario_name", "max_days"])
    writer.writeheader()
    writer.writerows(results)

print(f"Results saved to {csv_path}")
