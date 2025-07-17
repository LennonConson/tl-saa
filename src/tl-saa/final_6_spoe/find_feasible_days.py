import csv
import final_6_spoe
import pyomo.environ as pyo
import sys
import time

def find_min_days(scenario_name, replication, divisions_per_day=3, start_days=15, max_possible_days=30):
    """Find minimum days needed for feasibility by incrementing days until solution is optimal."""
    print(f"Processing {scenario_name}, replication {replication}...")
    
    for days in range(start_days, max_possible_days + 1):
        print(f"  Trying max_days = {days}")
        try:
            scenario_creator_kwargs = {
                "divisions_per_day": divisions_per_day,
                "max_days": days,
                "replication": replication
            }
            
            model = final_6_spoe.scenario_creator(scenario_name, **scenario_creator_kwargs)
            
            solver = pyo.SolverFactory('gurobi')
            solver.options['MIPGap'] = 0.99
            result = solver.solve(model, tee=False)
            
            status = result.solver.status
            condition = result.solver.termination_condition
            print(f"  Status: {status}, Condition: {condition}")
            
            if status == pyo.SolverStatus.ok and condition == pyo.TerminationCondition.optimal:
                print(f"  Found feasible solution at {days} days!")
                return scenario_name, replication, divisions_per_day, days, True
            
        except Exception as e:
            print(f"  Error with {days} days: {e}")
    
    # If we reach here, no feasible solution was found within the range
    print(f"  No feasible solution found up to {max_possible_days} days")
    return scenario_name, replication, divisions_per_day, max_possible_days, False

def main():
    start_time = time.time()
    
    # Parameters
    divisions_per_day = 3
    start_max_days = 15
    max_possible_days = 100
    
    # Get command line arguments for ranges if provided
    start_scen = 0
    end_scen = 99
    start_rep = 0
    end_rep = 99
    
    if len(sys.argv) > 2:
        start_scen = int(sys.argv[1])
        end_scen = int(sys.argv[2])
    if len(sys.argv) > 4:
        start_rep = int(sys.argv[3])
        end_rep = int(sys.argv[4])
    
    print(f"Processing scenarios {start_scen}-{end_scen}, replications {start_rep}-{end_rep}")
    
    # Open CSV file to write results as we go
    with open("feasibility_results.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["scenario_name", "replication", "divisions_per_day", "min_feasible_days", "is_feasible"])
        
        # Process each scenario and replication
        for scen_num in range(start_scen, end_scen + 1):
            scenario_name = f"scen{scen_num}"
            
            for rep in range(start_rep, end_rep + 1):
                result = find_min_days(
                    scenario_name, 
                    rep, 
                    divisions_per_day, 
                    start_max_days, 
                    max_possible_days
                )
                
                # Write result to CSV immediately
                writer.writerow(result)
                csvfile.flush()  # Ensure data is written immediately
    
    elapsed_time = time.time() - start_time
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")
    print(f"Results saved to feasibility_results.csv")

if __name__ == "__main__":
    main()