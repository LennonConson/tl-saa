from template_lshaed import run_lshaped
from datetime import datetime, timedelta
import time
import random
from pyomo.environ import *


solver = SolverFactory('gurobi')

t_solve = timedelta(days=0, hours=0, minutes=0, seconds=2)



# Update model parameters
# scenario_doe is 
tc_saa = {} # dicitionary in style of {(s, nu): 'optimality gap'}
tc_saa_replication = {} # dicitionary in style of {(s, nu, num_replications): objective_value}
for scenario_doe in range(1,2):
    a = {scenario_doe: [
        random.uniform(140, 160),
        random.uniform(220, 240),
        random.uniform(250, 270)
        ]}
    number_samples_in_SAA = 1

    for sample_explore in range(1,2):
        start_time = datetime.now()
        num_replication = 1
        while True:
            elapsed = datetime.now() - start_time
            remaining = t_solve - elapsed
            # Solve
            print("Remaining", remaining.total_seconds())
            if remaining.total_seconds() > 0:  # Success
                objective_value, status = run_lshaped(sample_explore, a[scenario_doe], solve_time_limit=remaining.total_seconds())
                if status == "optimal":
                    tc_saa_replication[(scenario_doe,number_samples_in_SAA,num_replication, status)] = objective_value
                    num_replication += 1
                    print(f"Remaining time: {remaining}; Replication {num_replication}; Result {objective_value}")

                else:
                    print("Ending with status: ", status)
            else:
                break
            

        #TODO OPTILITY GAP CALC
        optimality_gap =1
        tc_saa = {(scenario_doe, number_samples_in_SAA):optimality_gap}
        #TODO Put in adaptive
        number_samples_in_SAA += 10000
    
    
for (scenario_doe, sample, replication, opto), obj in tc_saa_replication.items():
    print(f"Scenario: {scenario_doe}, Sample: {sample}, Replication: {replication}, Opto: {opto} -> Objective: {obj:.6f}")
