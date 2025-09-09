import military_transshipment_port_selection_test36 as mtps
import pickle
import pyomo.environ as pyo
import time
from mpisppy.opt.lshaped import LShapedMethod
import csv
import os
import datetime

def solve_lshaped(outload_key, num_samples, replication, fix_solution=None):
    """
    Solve the L-shaped problem for given parameters.
    
    Args:
        outload_key (int): Key for selecting outload data
        num_samples (int): Number of scenarios to generate
        replication (int): Replication number
        fix_solution (dict, optional): Dictionary mapping y_open variable strings to fixed values
                                     e.g., {'y_open[6]': 0.0, 'y_open[7]': 1.0, 'y_open[8]': 0.0}
    
    Returns:
        tuple: (wall_clock_time, y_open_dict, obj, term)
    """
    print(f"Generating {num_samples} samples for replication {replication}.")

    with open("/home/user/git/tl-saa/data/outload_5_samples100.pkl", "rb") as f:
        all_outload = pickle.load(f)
    outload = all_outload[outload_key]
    print(f"Using outload key {outload_key}.")
    print(f"Outload: {outload}")
    all_scenario_names = [f"delay_scen{i}" for i in range(num_samples)]
    print(f"Scenario names: {all_scenario_names}")

    # Deterministic model creation and solving
    scenario_creator = mtps.scenario_creator
    scenario_creator_kwargs = {
        "divisions_per_day": 3,
        "outload": outload,
        "replication": replication,
        "max_days": 25,
        "total_number_of_samples": num_samples,
        "fix_solution": fix_solution
    }

    bounds = {name: -432000 for name in all_scenario_names}
    options = {
        "root_solver": "gurobi_persistent",
        "sp_solver": "gurobi_persistent",
        "sp_solver_options": {"threads": 16},
        "valid_eta_lb": bounds,
        "max_iter": 100
    }
    ls = LShapedMethod(options, all_scenario_names, scenario_creator, 
                       scenario_creator_kwargs=scenario_creator_kwargs)

    # Record start time
    start_time = time.time()

    try:
        result = ls.lshaped_algorithm()
        # Record end time and calculate elapsed time
        end_time = time.time()
        wall_clock_time = end_time - start_time

        variables = ls.gather_var_values_to_rank0()
        # Filter for 'delay_scen0' and keys starting with 'y_open'
        y_open_dict = {
            k[1]: v
            for k, v in variables.items()
            if k[0] == 'delay_scen0' and k[1].startswith('y_open')
        }
        obj = pyo.value(ls.root.obj)
        term = result['Solver'][0]['Termination condition']
        
        # Check if the solution is infeasible or unbounded
        if term in ['infeasible', 'unbounded', 'infeasibleOrUnbounded']:
            # Set default values for infeasible case
            y_open_dict = {k: 0.0 for k in y_open_dict.keys()}
            obj = 0.0
            term = "infeasible"

    except Exception as e:
        # Handle any errors during solving
        end_time = time.time()
        wall_clock_time = end_time - start_time
        
        # Set default values for error case
        y_open_dict = {'y_open[6]': 0.0, 'y_open[7]': 0.0, 'y_open[8]': 0.0, 
                       'y_open[9]': 0.0, 'y_open[10]': 0.0, 'y_open[11]': 0.0}
        obj = 0.0
        term = "infeasible"
        print(f"Error occurred: {e}")
    is_fixed = False
    if fix_solution is not None:
        is_fixed = True
    print("== =L-shaped Method Results ===")
    print(f"Wall clock time: {wall_clock_time:.2f} seconds")
    print(f"y_open_dict: {y_open_dict}")
    print(f"Objective: {obj}")
    print(f"Termination condition: {term}")
    print(f"Is first stage fixed: {is_fixed}")
    print("===============================")

    return wall_clock_time, y_open_dict, obj, term, is_fixed

def write_lshaped_results_to_csv(csv_file, outload_key, num_samples, replication, wall_clock_time, y_open_dict, obj, term, is_fixed, elapsed_time=None):
    fieldnames = [
        "outload_key", "num_samples", "replication", "wall_clock_time", "elapsed_time", "obj", "term", "is_fixed"
    ]
    # Add columns for each key in y_open_dict
    for k in y_open_dict.keys():
        if k not in fieldnames:
            fieldnames.append(k)

    row = {
        "outload_key": outload_key,
        "num_samples": num_samples,
        "replication": replication,
        "wall_clock_time": wall_clock_time,
        "elapsed_time": elapsed_time,
        "obj": obj,
        "term": term,
        "is_fixed": is_fixed
    }
    # Add y_open_dict values to the row
    for k, v in y_open_dict.items():
        row[k] = v

    # Write header only if file does not exist or is empty
    write_header = not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0

    with open(csv_file, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

if __name__ == "__main__":
    num_samples_set = [2, 3, 4, 5, 6, 7, 8, 9, 10, 20]  #
    num_outloads = 100
    csv_file = "/home/user/git/tl-saa/data/lshaped_results_test36.csv"
    max_minutes = 60

    # for outload_key in [range(num_outloads)]:
    for outload_key in [36]:
        print(f"\n=== Starting runs for outload_key={outload_key} ===")
        for num_samples in num_samples_set:
            print(f"\n=== Starting runs for num_samples={num_samples} ===")
            start_time = time.time()
            max_seconds = max_minutes * 60

            solution_set = set()
            replication = 0
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                print(f"Running replication {replication} (elapsed: {elapsed/60:.2f} min)")
                wall_clock_time, y_open_dict, obj, term, is_fixed = solve_lshaped(outload_key, num_samples, replication)

                current_time = time.time()
                elapsed = current_time - start_time
                write_lshaped_results_to_csv(
                    csv_file, outload_key, num_samples, replication, wall_clock_time, y_open_dict, obj, term, is_fixed, elapsed_time=elapsed
                )

                if replication > 0 and tuple(sorted(y_open_dict.items())) not in solution_set:
                    for prev_rep in range(replication):
                        wall_clock_time_fixed, y_open_dict_fixed, obj_fixed, term_fixed, is_fixed_fixed = solve_lshaped(
                            outload_key, num_samples, prev_rep, fix_solution=y_open_dict
                        )
                        current_time = time.time()
                        elapsed = current_time - start_time
                        write_lshaped_results_to_csv(
                            csv_file, outload_key, num_samples, prev_rep, wall_clock_time_fixed, y_open_dict_fixed, obj_fixed, term_fixed, is_fixed_fixed, elapsed_time=elapsed
                        )

                solution_set.add(tuple(sorted(y_open_dict.items())))
                # For each solution in solution_set except the current one, run solve_lshaped with fix_solution
                for prev_solution in solution_set:
                    if prev_solution == tuple(sorted(y_open_dict.items())):
                        continue
                    fix_solution = dict(prev_solution)
                    wall_clock_time_fixed, y_open_dict_fixed, obj_fixed, term_fixed, is_fixed_fixed = solve_lshaped(
                        outload_key, num_samples, replication, fix_solution=fix_solution
                    )
                    current_time = time.time()
                    elapsed = current_time - start_time
                    write_lshaped_results_to_csv(
                        csv_file, outload_key, num_samples, replication, wall_clock_time_fixed, y_open_dict_fixed, obj_fixed, term_fixed, is_fixed_fixed, elapsed_time=elapsed
                    )

                if elapsed >= max_seconds:
                    print(f"Reached {max_minutes} minutes for num_samples={num_samples}. Stopping loop.")
                    break
                replication += 1
