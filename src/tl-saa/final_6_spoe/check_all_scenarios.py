#### python
# filepath: /home/lennon/git/tl-saa/src/tl-saa/final_6_spoe/check_all_scenarios.py
import csv
import final_6_spoe
import pyomo.environ as pyo
import sys
import time

def solve_scenario(scenario_name):

    print(f"Solving {scenario_name}...")
    scenario_creator_kwargs = {
        "divisions_per_day": 3,
        "max_days": 16,
        "replication": 0
    }

    model = final_6_spoe.scenario_creator(scenario_name, **scenario_creator_kwargs)

    solver = pyo.SolverFactory('gurobi')
    solver.options['MIPGap'] = 0.9  # Stop when optimality gap is 50%
    result = solver.solve(model, tee=False)
    
    # Check if solution is optimal
    print(f"Status: {result.solver.status}, Termination Condition: {result.solver.termination_condition}")
        
    return scenario_name, result.solver.termination_condition

def main():
    
    # Create list of all scenario names
    scenario_names = [f"scen{i}" for i in range(100)]
    
    # Process scenarios sequentially
    print("Processing scenarios sequentially...")
    results = []
    for scenario_name in scenario_names:
        result = solve_scenario(scenario_name)
        results.append(result)

    with open("scenario_results.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["scenario_name", "termination_condition", "days", "division_per_day"])
        for scenario_name, status in results:
            writer.writerow([scenario_name, status, 20, 3])

if __name__ == "__main__":
    main()