import fixed_final_6_spoe
import pyomo.environ as pyo
import time
import csv
from itertools import combinations

scenario_creator = fixed_final_6_spoe.scenario_creator
scenario_creator_kwargs = {
    "divisions_per_day": 3,
    "replication": 0,
    "day_add": 0  # Adjust this if needed, currently set to 0
    }

# Generate all permutations where exactly 2 ports are open (1.0) and 4 are closed (0.0)
port_indices = [7, 8, 9, 10, 11, 12]  # Beaumont, Gulfport, Charleston, Jacksonville, Morehead City, Portsmouth
port_names = {7: "Beaumont", 8: "Gulfport", 9: "Charleston", 10: "Jacksonville", 11: "Morehead_City", 12: "Portsmouth"}

# Get all combinations of 2 ports from 6 ports
all_permutations = list(combinations(port_indices, 2))

for perm_idx, open_ports in enumerate(all_permutations):
    print(f"\n=== Processing permutation {perm_idx + 1}/{len(all_permutations)}: {[port_names[p] for p in open_ports]} ===")
    
    # Create solution_fix dictionary for this permutation
    solution_fix = {}
    for port in port_indices:
        if port in open_ports:
            solution_fix[port] = 1.0
        else:
            solution_fix[port] = 0.0
    
    # Create filename based on the permutation (1 for open, 0 for closed)
    filename_pattern = ""
    for port in port_indices:
        filename_pattern += "1" if port in open_ports else "0"
    filename = f"deterministic_optimal_results_{filename_pattern}.csv"
    
    print(f"Solution fix: {solution_fix}")
    print(f"Output file: {filename}")
    
    results = []

    for scen_num in range(100):  # scen0 to scen99
        scenario_name = f"scen{scen_num}"
        print(f"Using scenario: {scenario_name}")
        
        day_add = 0
        max_day_add = 40  # Prevent infinite loops, adjust as needed
        found_feasible = False
        
        while day_add <= max_day_add:
            scenario_creator_kwargs["day_add"] = day_add
            
            # Reinitialize the model for each attempt
            model = scenario_creator(scenario_name, **scenario_creator_kwargs)
            
            # Fix y_open values for specific ports using current permutation
            for i in model.y_open:
                if i in solution_fix:
                    model.y_open[i].fix(solution_fix[i])
                else:
                    model.y_open[i].fix(0.0)  # Fix other ports to 0.0

            solver = pyo.SolverFactory('gurobi')
            start_time = time.time()
            result = solver.solve(model, tee=False)
            wall_time = time.time() - start_time
            
            if (result.solver.status == pyo.SolverStatus.ok) and (result.solver.termination_condition == pyo.TerminationCondition.optimal):
                found_feasible = True
                break
            else:
                print(f"Infeasible for scenario {scenario_name} with day_add={day_add}, retrying...")
                # Delete the model object to free memory and ensure clean state
                del model
                day_add += 1

        if not found_feasible:
            print(f"Could not find feasible solution for scenario {scenario_name} within day_add limit.")
            y_open_values = {i: None for i in model.y_open}
            obj_value = None
        else:
            y_open_values = {i: pyo.value(model.y_open[i]) for i in model.y_open}
            obj_value = pyo.value(model.FirstStageCost)
            print(f"Scenario {scenario_name} solved in {wall_time:.2f} seconds with day_add={day_add}.")
            print(f"Objective value: {obj_value}")
            print(f"y_open values: {y_open_values}")

        # Flatten results for CSV
        row = {
            'scenario': scenario_name, 
            'wall_time': wall_time,
            'final_day_add': day_add if found_feasible else None,
            'objective_value': obj_value
        }
        row.update({f'y_open[{i}]': v for i, v in y_open_values.items()})
        results.append(row)

    # Write to CSV for this permutation
    fieldnames = ['scenario', 'wall_time', 'final_day_add', 'objective_value'] + [f'y_open[{i}]' for i in model.y_open]
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print(f"Completed permutation {filename_pattern} - saved to {filename}")

print("\n=== All permutations completed! ===")
print(f"Generated {len(all_permutations)} CSV files, one for each 2-port combination.")