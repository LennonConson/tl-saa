import pyomo.environ as pyo
import pandas as pd
import numpy as np
# Change imports for PH
from mpisppy.opt.ph import PH
import mpisppy.utils.sputils as sputils
from scenario_creator_rail_reduced import generate_rail_travel_times
from scenario_creator_ship_reduced import generate_ship_travel_times

def scenario_creator(scenario_name, **kwargs):
    scenario_doe      = kwargs["scenario_doe"]
    divisions_per_day = kwargs["divisions_per_day"]
    num_V             = kwargs["num_V"]
    
    
    # Build and return the Pyomo model.
    model = pyo.ConcreteModel()
    travel_time_by_rail = generate_rail_travel_times(divisions_per_day)
    ship_travel_times = generate_ship_travel_times(divisions_per_day, num_V)
    travel_times = {
            **travel_time_by_rail, 
            **ship_travel_times}

    max_days = 30
    divisions_per_day = 2
    u_open = 2
    num_I = 15
    num_J = 6
    num_K = 1
    num_V = 15
    num_T = divisions_per_day * max_days

    outload_requirements = {i + 1: val for i, val in enumerate(scenario_doe)}

    ship_layberth = {1:4, 2:4, 3:6, 4:6, # Bob Hope
                     5:6, 6:6, 7:6, 8:3, 9:6, 10:6, 11:6, # Watson
                     12:6, 13:6, # Gordon
                     14:6, 15:6} # Shughart
    updated_ship_layberth = {k: v + num_I for k, v in ship_layberth.items()}
    
    # Port Processing Limit
    daily_processing_rate_ft = {1: 119000, 2: 105000, 3: 109300, 4: 110000, 5: 88000, 6: 89300}
    SQFT_TO_SQM = 0.092903
    # Convert to square meters
    daily_processing_rate = {
        key: round(value * SQFT_TO_SQM)
        for key, value in daily_processing_rate_ft.items()
    }
    updated_daily_processing_rate = {k + num_I: v for k, v in daily_processing_rate.items()}
    

    ship_berth_binary = {}
    for ship, assigned_berth in updated_ship_layberth.items():
        for berth in range(num_I+1, num_I + num_J +1):
            if berth == assigned_berth:
                ship_berth_binary[(berth, ship)] = 1
            else:
                ship_berth_binary[(berth, ship)] = 0

    stowable_cargo_capacity = {1:35000, 2:35000, 3:35000, 4:35000, # Bob Hope
                        5:36511, 6:36511, 7:36511, 8:36511, 9:36511, 10:36511, 11:36511, # Watson
                        12:26390, 13:26390, # Gordon
                        14:29029, 15:29029} # Shughart

    # We need to have slightly more cargo space than possible outload
    FACTOR = 1.0001*24000*20/sum(stowable_cargo_capacity.values())

    scaled_stowable_cargo_capacity = {
        key: round(value * FACTOR)
        for key, value in stowable_cargo_capacity.items()
    }
    


    
    # Sets
    # --------------
    # I the set of origins
    model.I = pyo. Set(initialize = range(1, num_I+1))
    # J the set of transshipment nodes/SPOEs
    model.J = pyo.Set(initialize = range(num_I + 1 , num_I +num_J+1))
    model.J_0 = pyo.Set(initialize = [0]+ list(range(num_I + 1 , num_I +num_J+1)))
    # # K the set of destinations/SPODs
    model.K = pyo.Set(initialize = range(num_I +num_J+1, num_I + num_J + num_K+1))
    # # # JK the set of destinations/SPODs
    model.M = pyo.Set(initialize = range(num_I +1, num_I + num_J + num_K+1))
    # # # IJK the set of destinations/SPODs
    model.N = pyo.Set(initialize = range(1, num_I + num_J + num_K+1))

    model.N_0 = pyo.Set(initialize = range(num_I + num_J + num_K+1))

    # model.N_0 = pyo.Set(initialize = range( num_I + num_J + num_K+1))
    # # V the set of ships
    model.V = pyo.Set(initialize = range(1,num_V+1))
    # # V the set of ships
    model.V_0 = pyo.Set(initialize = range(num_V+1))
    # # T the set of ships
    model.T = pyo.Set(initialize = range(1, num_T+1))
    model.T_0 = pyo.Set(initialize = range(num_T+1))
    model.D = pyo.Set(initialize = range(1,max_days+1))

    # # Parameters
    # # ---------
    # # Outload Requirements
    model.a_i  = pyo.Param(model.I,           initialize=outload_requirements, within=pyo.NonNegativeReals)
    # # Outload Requirements
    model.b_jv  = pyo.Param(model.J, model.V,           initialize=ship_berth_binary,  within=pyo.NonNegativeReals)
    # Travel Times
    model.c_nnv  = pyo.Param(model.N_0, model.N, model.V_0,           initialize=travel_times, within=pyo.NonNegativeReals)
    # tau days number of time windows per day
    # model.tau   = pyo.Param(                    initialize=divisions_per_day, within=pyo.NonNegativeReals)
    # maximum number of spoes
    model.u_open   = pyo.Param(                    initialize=u_open, within=pyo.NonNegativeReals)
    # Stowable Cargo Capacity
    model.u_ship   = pyo.Param(model.V,                    initialize=scaled_stowable_cargo_capacity, within=pyo.NonNegativeReals)
    # Daily Processing Rate
    model.u_spoe   = pyo.Param(model.J,                    initialize=updated_daily_processing_rate, within=pyo.NonNegativeReals)
    model.FirstStageCost = 0

    max_travel = max(
        model.c_nnv[index] 
        for index in model.c_nnv
    )
    

    model.T_prime = pyo.Set(initialize = range(num_T+max_travel+1))

    # Define Decision Variables
    # ------------------------
    # Utilization of port J
    model.y_open     = pyo.Var(model.J, domain=pyo.Binary, initialize=0)
    # The amount of equipment that arrives at time T from/at/to IJK
    model.x_rail  = pyo.Var(model.I, model.J, model.T, domain=pyo.NonNegativeReals, initialize=0)
    model.y_rail  = pyo.Var(model.I, model.J, model.T, domain=pyo.Binary, initialize=0)
    # model.x_ship_in  = pyo.Var(model.J_0, model.M, model.K, model.V, model.T_0, domain=pyo.NonNegativeReals, initialize=0)
    # The amount of equipment that arrives at time T from/at/to IJK
    model.x_ship_out = pyo.Var(model.J_0, model.M, model.V, model.T_0, domain=pyo.NonNegativeReals, initialize=0)
    # The amount of equipment that arrives at time T from/at/to IJK
    # model.y_ship_in  = pyo.Var(model.J_0, model.M, model.K, model.V, model.T_0, domain=pyo.Binary, initialize=0)
    model.y_ship_out = pyo.Var(model.J_0, model.M, model.V, model.T_0, domain=pyo.Binary, initialize=0)
    # model.active_ship_k = pyo.Var(model.K, model.V, domain=pyo.Binary, initialize=0)

    # Objective Funtion
    def objective_rule(model):
        return sum((model.c_nnv[j,k,v] + t) * model.x_ship_out[j,k,v,t] for j in model.J for k in model.K for v in model.V for t in model.T)
    model.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

    # TIER 1 TASK: Connect x-rail to y-rail
    # STATUS: V&V
    # 21
    def const_x_rail_to_y(model, i, j, t):
        return model.x_rail[i,j,t]  <= model.u_spoe[j] * model.y_rail[i,j,t]
    model.const_x_rail_to_y = pyo.Constraint(model.I, model.J, model.T, rule=const_x_rail_to_y)

    # TIER 1 TASK: Ship connect x to y
    # STATUS: V&V
    # TODO: Fix M
    # 22
    def const_x_ship_out_to_y(model, j, m, v,t):
        return model.x_ship_out[j,m,v,t]  <= model.u_ship[v] * model.y_ship_out[j,m,v,t]
    model.const_x_ship_out_to_y = pyo.Constraint(model.J, model.M, model.V, model.T, rule=const_x_ship_out_to_y)

    #############
    # ENTITY: SPOE
    #############
    # TIER 1 TASK: Check max spoes are opened
    # STATUS: V&V
    # 23
    def const_u_spoe(model):
        return sum(model.y_open[j] for j in model.J) <= model.u_open
    model.const_u_spoe = pyo.Constraint(rule=const_u_spoe)

    # # TIER 1 TASK: Make sure only use open ports
    # # STATUS: V&V
    # # 24
    def const_only_open_rail(model, i, j, t):
        return  model.y_rail[i,j,t] <= model.y_open[j]
    model.const_only_open_rail = pyo.Constraint(model.I, model.J, model.T, rule=const_only_open_rail)

    # # # 25
    # def const_only_open_ship_out(model, j, m, v, t):
    #     return  model.y_ship_out[j,m,v,t] <= model.y_open[j]
    # model.const_only_open_ship_out = pyo.Constraint(model.J, model.M, model.V, model.T, rule=const_only_open_ship_out)

    # 26
    def const_only_open_ship_in(model, j, j_prime, v, t):
        return  model.y_ship_out[j,j_prime,v,t] <= model.y_open[j_prime]
    model.const_only_open_ship_in = pyo.Constraint(model.J, model.J, model.V, model.T, rule=const_only_open_ship_in)


    ##############
    # ENTITY: Rail
    ##############


    # TIER 1 TASK: Make sure all rolling stock departs I.
    # STATUS: V&V
    # 27
    def cont_outload(model, i):
        return sum(model.x_rail[i,j,t] for j in model.J for t in model.T) == model.a_i[i]
    model.cont_outload = pyo.Constraint(model.I, rule=cont_outload)

    # TIER 1 TASK: Make sure daily processing is observed
    # STATUS: V&V
    # 28
    def const_daily_processing(model, j, d):
            return sum(model.x_rail[i,j,t]
                    for i in model.I
                    for t in range(divisions_per_day  * (d - 1) +1, divisions_per_day  * d))  <= model.u_spoe[j]
    model.const_daily_processing = pyo.Constraint(model.J, model.D, rule=const_daily_processing)

    # TIER 1 TASK: Make sure that a ship does not depart before the begining of time horizon.
    # STATUS: V&V
    # 29
    def const_start_time(model, i, j, t):
        if t > model.c_nnv[i,j,0]:
            return pyo.Constraint.Skip
        return model.y_rail[i, j, t] == 0
    model.const_start_time= pyo.Constraint(model.I, model.J, model.T, rule=const_start_time)

    ##############
    # ENTITY: Ship
    ##############

    # TIER 1 TASK: Ship Pathing
    # STATUS: V&V

    # TIER 2 TASK: Set layberth port
    # STATUS: V&V
    # 30
    def const_layberth(model, j, v):
        return model.y_ship_out[0, j, v, 0] == model.b_jv[j,v]
    model.const_layberth = pyo.Constraint(model.J, model.V, rule=const_layberth)

    # TIER 2 TASK: Ensure SPOE 0 is not used outside of time 0.
    # STATUS: V&V
    # 31
    def const_illegal_layberth_out(model):
        return sum(
            model.y_ship_out[0, m, v, t]
            for m in model.M
            for v in model.V
            for t in model.T
        ) == 0
    model.const_illegal_layberth_out = pyo.Constraint(rule=const_illegal_layberth_out)

    # TIER 2 TASK: Ensure at time 0 only layberths origins are used.
    # STATUS: V&V
    # 32
    def const_illegal_time_0(model):
        return sum(
            model.y_ship_out[j, m, v, 0]
            for j in model.J
            for m in model.M
            for v in model.V
        ) == 0
    model.const_illegal_time_0 = pyo.Constraint(rule=const_illegal_time_0)

    # TIER 2 TASK: Ensure that all ships that go through a J go somewhere.
    # STATUS: V&V
    # 33
    def const_intermediate_nodes(model, j, v):
        return (
            sum(model.y_ship_out[j_prime, j, v, t] for j_prime in model.J_0 if j_prime != j for t in model.T_0)
            == sum(model.y_ship_out[j, m, v, t] for m in model.M if m != j for t in model.T)
        )
    model.const_intermediate_nodes = pyo.Constraint(model.J, model.V, rule=const_intermediate_nodes)


    # TIER 2 TASK: Ensure that all ships go to SPOD once.
    # STATUS: V&V
    # 34
    def const_destination_nodes(model, v):
        return (sum(model.y_ship_out[j, k, v, t] for j in model.J for k in model.K for t in model.T)
                == 1)
    model.const_destination_nodes = pyo.Constraint(model.V, rule=const_destination_nodes)


    # TIER 1 TASK: Ship Capacity
    # STATUS: V&V
    # 35
    def const_ship_capacity(model, v, t):
        return sum(model.x_ship_out[j,m,v,t] for j  in model.J for m in model.M if j != m ) <= model.u_ship[v]
    model.const_ship_capacity = pyo.Constraint(model.V, model.T, rule=const_ship_capacity)


    ##############
    # ENTITY: Time
    ##############

    # TIER 1 TASK: Make sure ships have time to reach destination within time horizon.
    # STATUS: V&V
    # 36
    def const_time_to_reach_m(model, j, m, v, t):
        if j == m or t < num_T - model.c_nnv[j,m,v]:
            return pyo.Constraint.Skip  # Skip constraint when j equals j_prime0
        return model.y_ship_out[j, m, v, t] == 0
    model.const_time_to_reach_m = pyo.Constraint(model.J, model.M, model.V, model.T, rule=const_time_to_reach_m)

    # TIER 1 TASK: Make sure arrive before they depart.
    # STATUS: V&V
    # 37
    def const_ship_timing(model, j, v):
        return (
            sum((t+model.c_nnv[j_prime,j,v]+1)* model.y_ship_out[j_prime,j, v, t]
                for j_prime in model.J_0 if j != j_prime
                for t in model.T_0 if t >= model.c_nnv[j_prime, j, v])
                <=
                sum(
                    t * model.y_ship_out[j, m, v, t]
                    for m in model.M if j != m
                    for t in model.T if t <= num_T -model.c_nnv[j, m, v]))
    model.const_ship_timing = pyo.Constraint(model.J, model.V, rule=const_ship_timing)


    # ##############
    # # ENTITY: Supply Snchronization
    # ##############
    # TIER 1 TASK: Ship Reach Destination
    # STATUS: V&V
    # 38
    def const_reach_destination(model, k):
        return (sum(model.x_ship_out[j,k,v,t] for j in model.J for v in model.V for t in model.T)
                == sum(model.a_i[i] for i in model.I))
    model.const_reach_destination = pyo.Constraint(model.K, rule=const_reach_destination)

    # TIER 1 TASK: Overall supply balance
    # STATUS: V&V
    # 39
    def const_flow_balance(model, j):
        return (sum(model.x_rail[i,j,t] for i in model.I for t in model.T)
                + sum(model.x_ship_out[j_prime,j,v,t] for j_prime in model.J if j != j_prime for v in  model.V for t in model.T)
                == sum(model.x_ship_out[j,m,v,t] for m in model.M if m != j for v in model.V for t in model.T))
    model.const_flow_balance = pyo.Constraint(model.J, rule=const_flow_balance)

    # TIER 1 TASK: Time supply balance
    # STATUS: V&V
    # 40
    def const_const_supply(model, j, t):
        return (sum(model.x_rail[i,j,t_prime] for i in model.I for t_prime in range(1,t))
                + sum(model.x_ship_out[j_prime,j,v,t_prime] for j_prime in model.J if j != j_prime for v in  model.V for t_prime in range(1,t) if t_prime + model.c_nnv[j_prime, j, v] + 1 <= t)
                >= sum(model.x_ship_out[j,m,v,t_prime] for m in model.M if m != j for v in model.V for t_prime in range(1,t+1)))
    model.const_const_supply = pyo.Constraint(model.J, model.T, rule=const_const_supply)

    # TIER 1 TASK: Make sure there is ship storage
    # STATUS: V&V
    def const_storage(model, j, t):
        return (   sum(                  model.x_rail[i,j,t_prime] for i in model.I for t_prime in range(1,t+1))
                +  sum(                  model.x_ship_out[j_prime,j,v,t_prime]
                    for j_prime in model.J_0 if j != j_prime
                    for v in  model.V
                    for t_prime in range(0,t) if t_prime + model.c_nnv[j_prime, j, v] <= t)
                -  sum(                  model.x_ship_out[j,m,v,t_prime] for m in model.M if m != j for v in model.V for t_prime in range(1,t+1))
                <= sum(model.u_ship[v] * model.y_ship_out[j_prime,j,v,t_prime]
                    for j_prime in model.J_0 if j != j_prime 
                    for v in model.V
                    for t_prime in range(0,t) if t_prime + model.c_nnv[j_prime, j, v] <= t)
                -  sum(model.u_ship[v] * model.y_ship_out[j,m,v,t_prime] for m in model.M if m != j for v in model.V for t_prime in range(1,t+1)))
    model.const_storage = pyo.Constraint(model.J, model.T, rule=const_storage)


    # TIER 1 TASK: Make sure there is ship storage
    # STATUS: V&V
    def const_ship_mono(model, j, v):
        return (sum(model.x_ship_out[j_prime,j,v,t] for j_prime in model.J_0 if j != j_prime  for t in model.T_0)
                <= sum(model.x_ship_out[j,m,v,t] for m in model.M if j != m for t in model.T))
    model.const_ship_mono = pyo.Constraint(model.J,model.V, rule=const_ship_mono)

    sputils.attach_root_node(model, model.FirstStageCost, [model.y_open])
    return model

def scenario_denouement(rank, scenario_name, scenario):
    pass

def run_lshaped(num_scenarios, scenario_doe, solve_time_limit):
    
    scenario_creator_kwargs = {
        "scenario_doe": scenario_doe,
        "divisions_per_day": 2,
        "num_V": 15
    }
    all_scenario_names = list(range(1, num_scenarios + 1))
    
    # PH options differ from L-shaped
    options = {
        "solver_name": "gurobi_persistent",
        "solver_options": {
            "threads": 1,
            "MIPGap": 0.01
        },
        # For iteration 0 (first solve)
        "iter0_solver_options": {
            "threads": 1,
            "MIPGap": 0.01
        },
        # Add this missing required option for iterations 1 and beyond
        "iterk_solver_options": {
            "threads": 1,
            "MIPGap": 0.01  # Can be looser for later iterations if desired
        },
        # PH specific parameters
        "PHIterLimit": 50,  # Max PH iterations
        "defaultPHrho": 10.0,  # Default rho value
        "convthresh": 1e-6,  # Convergence threshold
        "verbose": True,
        "display_timing": True,
        "display_progress": True,
        # Integer variable options for PH
        "linearize_binary_proximal_terms": True,  # Better for binary variables
        "breakpoint_strategy": 0,
        "xhat_method": "closest_scenario",  # Method for computing xhat
        "xhat_scenario_dict": None,  # Will be computed automatically
        "suppress_warnings": False
    }
    
    # Initialize the PH object instead of L-shaped
    ph = PH(
        options,
        all_scenario_names,
        scenario_creator,
        scenario_denouement,
        scenario_creator_kwargs=scenario_creator_kwargs
    )
    
    # Run PH algorithm
    conv, obj, tbound = ph.ph_main()
    
    # Get solution from xhat
    try:
        # Try to get y_open values from xhat (can change based on PH implementation)
        sol = {k: ph.xhat["ROOT"][k] for k in ph.scenario_dendro["ROOT"].nonleaves[0].scen.y_open}
    except:
        # Alternatively get from a scenario's solution
        a_scenario = ph.local_scenarios[all_scenario_names[0]]
        sol = {k: a_scenario.y_open[k].value for k in a_scenario.y_open}
    
    # Get objective value and termination status
    obj_val = obj  # PH returns the objective value directly
    term = "optimal" if conv else "iteration_limit"
    
    return obj_val, term, sol