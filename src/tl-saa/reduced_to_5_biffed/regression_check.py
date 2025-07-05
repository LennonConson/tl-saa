import pyomo.environ as pyo
import numpy as np
import math
import random
import mpisppy.utils.sputils as sputils
from mpisppy.spin_the_wheel import WheelSpinner
from mpisppy.utils import config
import mpisppy.utils.cfg_vanilla as vanilla
from mpisppy.cylinders.hub import LShapedHub
from mpisppy.opt.lshaped import LShapedMethod
import mpisppy.utils.cfg_vanilla as vanilla
from mpisppy.cylinders.hub import LShapedHub
from mpisppy.opt.lshaped import LShapedMethod
from scenario_creator_rail_reduced import generate_rail_travel_times
from scenario_creator_ship_reduced import generate_ship_travel_times


# np.random.seed(42)
# random.seed(42)

def build_model(travel_times):
    scenario_doe = [19500.0, 19500.0, 19500.0, 19500.0, 19500.0, 19500.0, 19500.0, 19500.0, 19500.0, 19500.0]
    
    
    
    
    # Build and return the Pyomo model.
    model = pyo.ConcreteModel()


    max_days = 30
    divisions_per_day = 2
    u_open = 1
    num_I = 10
    num_J = 5
    num_K = 1
    num_V = 15
    num_T = divisions_per_day * max_days

    outload_requirements = {i + 1: val for i, val in enumerate(scenario_doe)}

    # ship_layberth = {1:3, 2:3, 3:5, 4:5, # Bob Hope
    #                  5:5, 6:5, 7:5, 8:3, 9:5, 10:5, 11:5, # Watson
    #                  12:5, 13:5, # Gordon
    #                  14:5, 15:5} # Shughart
    ship_layberth = {1:1, 2:2, 3:3, 4:4, # Bob Hope
                5:5, 6:6, 7:1, 8:2, 9:3, 10:4, 11:5, # Watson
                12:6, 13:1, # Gordon
                14:3, 15:5} # Shughart
    # 21 → X
    # 22 → 11
    # 23 → 12
    # 24 → 13
    # 25 → 14
    # 26 → 15
    # 27 → 16
    # 28 → X
    # 29 → X
    # 30 → X
    # 31 → 17
    updated_ship_layberth = {k: v + num_I for k, v in ship_layberth.items()}
    
    # Port Processing Limit
    daily_processing_rate_ft = {1: 105000, 2: 109300, 3: 110000, 4: 88000, 5: 89300}
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
    FACTOR = 1.0001*24000*num_V/sum(stowable_cargo_capacity.values())

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
    return model



def perturb_travel_time(mean_travel_time):
    perturbed_travel_time = {}
    sigma = 0.1
    for key in mean_travel_time:
        mu = math.log(mean_travel_time[key])
        perturbed_travel_time[key] = round(np.random.lognormal(mean=mu, sigma=sigma))
    return perturbed_travel_time


def perturb_parameters():
    travel_time_by_rail = {(1, 1): 1, (1, 2): 8, (1, 3): 12, (1, 4): 11, (1, 5): 12, (1, 6): 15, (1, 7): 14, (1, 8): 12, (1, 9): 10, (1, 10): 18, (2, 1): 19, (2, 2): 23, (2, 3): 27, (2, 4): 21, (2, 5): 25, (2, 6): 22, (2, 7): 7, (2, 8): 9, (2, 9): 12, (2, 10): 1, (3, 1): 5, (3, 2): 5, (3, 3): 7, (3, 4): 6, (3, 5): 8, (3, 6): 6, (3, 7): 19, (3, 8): 19, (3, 9): 19, (3, 10): 17, (4, 1): 8, (4, 2): 11, (4, 3): 13, (4, 4): 13, (4, 5): 19, (4, 6): 17, (4, 7): 10, (4, 8): 7, (4, 9): 8, (4, 10): 13, (5, 1): 15, (5, 2): 14, (5, 3): 21, (5, 4): 20, (5, 5): 21, (5, 6): 24, (5, 7): 8, (5, 8): 4, (5, 9): 1, (5, 10): 9, (6, 1): 7, (6, 2): 8, (6, 3): 4, (6, 4): 2, (6, 5): 4, (6, 6): 6, (6, 7): 23, (6, 8): 21, (6, 9): 22, (6, 10): 23, (7, 1): 11, (7, 2): 8, (7, 3): 1, (7, 4): 2, (7, 5): 4, (7, 6): 1, (7, 7): 22, (7, 8): 24, (7, 9): 21, (7, 10): 27, (8, 1): 9, (8, 2): 9, (8, 3): 11, (8, 4): 11, (8, 5): 9, (8, 6): 9, (8, 7): 17, (8, 8): 20, (8, 9): 18, (8, 10): 13, (9, 1): 6, (9, 2): 10, (9, 3): 15, (9, 4): 13, (9, 5): 20, (9, 6): 16, (9, 7): 9, (9, 8): 11, (9, 9): 10, (9, 10): 9, (10, 1): 10, (10, 2): 8, (10, 3): 1, (10, 4): 7, (10, 5): 4, (10, 6): 4, (10, 7): 25, (10, 8): 24, (10, 9): 21, (10, 10): 25, (11, 1): 7, (11, 2): 6, (11, 3): 8, (11, 4): 8, (11, 5): 8, (11, 6): 5, (11, 7): 20, (11, 8): 20, (11, 9): 19, (11, 10): 17, (12, 1): 8, (12, 2): 5, (12, 3): 9, (12, 4): 11, (12, 5): 10, (12, 6): 10, (12, 7): 15, (12, 8): 15, (12, 9): 14, (12, 10): 15, (13, 1): 14, (13, 2): 11, (13, 3): 5, (13, 4): 9, (13, 5): 7, (13, 6): 6, (13, 7): 24, (13, 8): 21, (13, 9): 21, (13, 10): 21, (14, 1): 12, (14, 2): 11, (14, 3): 8, (14, 4): 6, (14, 5): 6, (14, 6): 1, (14, 7): 21, (14, 8): 23, (14, 9): 22, (14, 10): 21, (15, 1): 2, (15, 2): 3, (15, 3): 10, (15, 4): 8, (15, 5): 11, (15, 6): 10, (15, 7): 17, (15, 8): 13, (15, 9): 13, (15, 10): 20, (16, 1): 5, (16, 2): 8, (16, 3): 10, (16, 4): 12, (16, 5): 16, (16, 6): 15, (16, 7): 13, (16, 8): 16, (16, 9): 13, (16, 10): 20, (17, 1): 13, (17, 2): 15, (17, 3): 23, (17, 4): 18, (17, 5): 22, (17, 6): 23, (17, 7): 4, (17, 8): 4, (17, 9): 3, (17, 10): 11, (18, 1): 8, (18, 2): 7, (18, 3): 5, (18, 4): 7, (18, 5): 5, (18, 6): 6, (18, 7): 20, (18, 8): 17, (18, 9): 17, (18, 10): 18, (19, 1): 6, (19, 2): 5, (19, 3): 11, (19, 4): 12, (19, 5): 12, (19, 6): 11, (19, 7): 17, (19, 8): 16, (19, 9): 13, (19, 10): 17, (20, 1): 4, (20, 2): 3, (20, 3): 7, (20, 4): 7, (20, 5): 8, (20, 6): 8, (20, 7): 18, (20, 8): 18, (20, 9): 18, (20, 10): 21}
    travel_time_by_ship_to_spoe = {(1, 1): 67, (2, 1): 50, (3, 1): 24, (4, 1): 32, (5, 1): 22, (6, 1): 36, (7, 1): 35, (8, 1): 36, (9, 1): 33, (10, 1): 36, (11, 1): 34, (12, 1): 76, (13, 1): 75, (14, 1): 76, (15, 1): 67, (16, 1): 79, (17, 1): 68, (18, 1): 78, (19, 1): 22, (20, 1): 21, (21, 1): 76, (22, 1): 36, (23, 1): 35, (24, 1): 33, (25, 1): 18, (26, 1): 20, (27, 1): 19, (28, 1): 19, (29, 1): 17, (30, 1): 39, (31, 1): 37, (32, 1): 50, (33, 1): 31, (34, 1): 20, (35, 1): 19, (36, 1): 20, (37, 1): 18, (38, 1): 20, (39, 1): 31, (40, 1): 66, (1, 3): 65, (2, 3): 49, (3, 3): 28, (4, 3): 22, (5, 3): 28, (6, 3): 20, (7, 3): 20, (8, 3): 18, (9, 3): 17, (10, 3): 20, (11, 3): 19, (12, 3): 75, (13, 3): 75, (14, 3): 74, (15, 3): 65, (16, 3): 77, (17, 3): 65, (18, 3): 79, (19, 3): 35, (20, 3): 35, (21, 3): 76, (22, 3): 22, (23, 3): 23, (24, 3): 21, (25, 3): 36, (26, 3): 33, (27, 3): 35, (28, 3): 35, (29, 3): 34, (30, 3): 28, (31, 3): 27, (32, 3): 52, (33, 3): 22, (34, 3): 28, (35, 3): 27, (36, 3): 29, (37, 3): 30, (38, 3): 30, (39, 3): 21, (40, 3): 68, (1, 2): 62, (2, 2): 47, (3, 2): 18, (4, 2): 31, (5, 2): 19, (6, 2): 33, (7, 2): 34, (8, 2): 35, (9, 2): 33, (10, 2): 34, (11, 2): 34, (12, 2): 69, (13, 2): 70, (14, 2): 71, (15, 2): 66, (16, 2): 78, (17, 2): 67, (18, 2): 79, (19, 2): 18, (20, 2): 18, (21, 2): 69, (22, 2): 34, (23, 2): 33, (24, 2): 35, (25, 2): 22, (26, 2): 21, (27, 2): 24, (28, 2): 23, (29, 2): 24, (30, 2): 39, (31, 2): 37, (32, 2): 47, (33, 2): 29, (34, 2): 22, (35, 2): 24, (36, 2): 24, (37, 2): 22, (38, 2): 21, (39, 2): 32, (40, 2): 65, (1, 4): 63, (2, 4): 50, (3, 4): 26, (4, 4): 23, (5, 4): 25, (6, 4): 22, (7, 4): 23, (8, 4): 21, (9, 4): 24, (10, 4): 22, (11, 4): 21, (12, 4): 74, (13, 4): 74, (14, 4): 74, (15, 4): 67, (16, 4): 79, (17, 4): 67, (18, 4): 80, (19, 4): 29, (20, 4): 31, (21, 4): 75, (22, 4): 26, (23, 4): 28, (24, 4): 26, (25, 4): 34, (26, 4): 34, (27, 4): 34, (28, 4): 33, (29, 4): 33, (30, 4): 28, (31, 4): 28, (32, 4): 50, (33, 4): 22, (34, 4): 25, (35, 4): 28, (36, 4): 30, (37, 4): 31, (38, 4): 30, (39, 4): 23, (40, 4): 67, (1, 5): 67, (2, 5): 49, (3, 5): 27, (4, 5): 23, (5, 5): 26, (6, 5): 21, (7, 5): 24, (8, 5): 22, (9, 5): 22, (10, 5): 22, (11, 5): 22, (12, 5): 73, (13, 5): 75, (14, 5): 73, (15, 5): 65, (16, 5): 78, (17, 5): 65, (18, 5): 77, (19, 5): 36, (20, 5): 35, (21, 5): 76, (22, 5): 22, (23, 5): 21, (24, 5): 23, (25, 5): 38, (26, 5): 37, (27, 5): 38, (28, 5): 40, (29, 5): 37, (30, 5): 21, (31, 5): 21, (32, 5): 49, (33, 5): 23, (34, 5): 27, (35, 5): 26, (36, 5): 32, (37, 5): 31, (38, 5): 30, (39, 5): 18, (40, 5): 68, (1, 7): 18, (2, 7): 17, (3, 7): 46, (4, 7): 49, (5, 7): 48, (6, 7): 84, (7, 7): 84, (8, 7): 84, (9, 7): 81, (10, 7): 82, (11, 7): 83, (12, 7): 20, (13, 7): 17, (14, 7): 17, (15, 7): 24, (16, 7): 27, (17, 7): 22, (18, 7): 26, (19, 7): 74, (20, 7): 75, (21, 7): 19, (22, 7): 75, (23, 7): 76, (24, 7): 75, (25, 7): 82, (26, 7): 84, (27, 7): 81, (28, 7): 81, (29, 7): 81, (30, 7): 81, (31, 7): 82, (32, 7): 17, (33, 7): 49, (34, 7): 49, (35, 7): 50, (36, 7): 58, (37, 7): 59, (38, 7): 59, (39, 7): 64, (40, 7): 28, (1, 8): 22, (2, 8): 22, (3, 8): 47, (4, 8): 50, (5, 8): 45, (6, 8): 78, (7, 8): 77, (8, 8): 77, (9, 8): 79, (10, 8): 77, (11, 8): 78, (12, 8): 22, (13, 8): 23, (14, 8): 24, (15, 8): 20, (16, 8): 29, (17, 8): 18, (18, 8): 32, (19, 8): 72, (20, 8): 71, (21, 8): 23, (22, 8): 70, (23, 8): 72, (24, 8): 72, (25, 8): 77, (26, 8): 80, (27, 8): 80, (28, 8): 80, (29, 8): 77, (30, 8): 77, (31, 8): 79, (32, 8): 23, (33, 8): 52, (34, 8): 47, (35, 8): 46, (36, 8): 59, (37, 8): 60, (38, 8): 59, (39, 8): 58, (40, 8): 26, (1, 6): 66, (2, 6): 52, (3, 6): 28, (4, 6): 20, (5, 6): 26, (6, 6): 21, (7, 6): 22, (8, 6): 23, (9, 6): 24, (10, 6): 23, (11, 6): 24, (12, 6): 75, (13, 6): 75, (14, 6): 73, (15, 6): 67, (16, 6): 82, (17, 6): 67, (18, 6): 81, (19, 6): 36, (20, 6): 36, (21, 6): 74, (22, 6): 18, (23, 6): 20, (24, 6): 20, (25, 6): 40, (26, 6): 38, (27, 6): 39, (28, 6): 38, (29, 6): 39, (30, 6): 18, (31, 6): 18, (32, 6): 51, (33, 6): 17, (34, 6): 30, (35, 6): 29, (36, 6): 29, (37, 6): 30, (38, 6): 31, (39, 6): 20, (40, 6): 67, (1, 9): 23, (2, 9): 21, (3, 9): 48, (4, 9): 47, (5, 9): 47, (6, 9): 73, (7, 9): 76, (8, 9): 73, (9, 9): 73, (10, 9): 76, (11, 9): 74, (12, 9): 22, (13, 9): 24, (14, 9): 24, (15, 9): 18, (16, 9): 31, (17, 9): 18, (18, 9): 30, (19, 9): 69, (20, 9): 71, (21, 9): 23, (22, 9): 65, (23, 9): 66, (24, 9): 67, (25, 9): 75, (26, 9): 74, (27, 9): 75, (28, 9): 75, (29, 9): 74, (30, 9): 73, (31, 9): 73, (32, 9): 21, (33, 9): 48, (34, 9): 47, (35, 9): 46, (36, 9): 55, (37, 9): 54, (38, 9): 56, (39, 9): 57, (40, 9): 32, (1, 10): 26, (2, 10): 21, (3, 10): 53, (4, 10): 55, (5, 10): 56, (6, 10): 89, (7, 10): 90, (8, 10): 91, (9, 10): 92, (10, 10): 89, (11, 10): 92, (12, 10): 25, (13, 10): 26, (14, 10): 25, (15, 10): 32, (16, 10): 19, (17, 10): 31, (18, 10): 20, (19, 10): 88, (20, 10): 86, (21, 10): 28, (22, 10): 83, (23, 10): 82, (24, 10): 81, (25, 10): 93, (26, 10): 94, (27, 10): 95, (28, 10): 95, (29, 10): 95, (30, 10): 91, (31, 10): 90, (32, 10): 24, (33, 10): 53, (34, 10): 56, (35, 10): 53, (36, 10): 68, (37, 10): 66, (38, 10): 65, (39, 10): 68, (40, 10): 17}
    travel_time_by_ship_to_spod = {(1, 1, 1): 46, (1, 1, 2): 32, (1, 1, 3): 30, (1, 1, 4): 31, (1, 1, 5): 29, (1, 1, 6): 66, (1, 1, 7): 68, (1, 1, 8): 67, (1, 1, 9): 66, (1, 1, 10): 67, (1, 1, 11): 65, (1, 1, 12): 57, (1, 1, 13): 58, (1, 1, 14): 60, (1, 1, 15): 54, (1, 1, 16): 55, (1, 1, 17): 54, (1, 1, 18): 53, (1, 1, 19): 63, (1, 1, 20): 61, (1, 1, 21): 59, (1, 1, 22): 53, (1, 1, 23): 56, (1, 1, 24): 54, (1, 1, 25): 65, (1, 1, 26): 66, (1, 1, 27): 68, (1, 1, 28): 65, (1, 1, 29): 68, (1, 1, 30): 61, (1, 1, 31): 64, (1, 1, 32): 29, (1, 1, 33): 32, (1, 1, 34): 32, (1, 1, 35): 32, (1, 1, 36): 43, (1, 1, 37): 44, (1, 1, 38): 44, (1, 1, 39): 41, (1, 1, 40): 43, (1, 2, 1): 89, (1, 2, 2): 58, (1, 2, 3): 57, (1, 2, 4): 59, (1, 2, 5): 57, (1, 2, 6): 126, (1, 2, 7): 126, (1, 2, 8): 127, (1, 2, 9): 125, (1, 2, 10): 128, (1, 2, 11): 128, (1, 2, 12): 112, (1, 2, 13): 111, (1, 2, 14): 110, (1, 2, 15): 101, (1, 2, 16): 101, (1, 2, 17): 101, (1, 2, 18): 104, (1, 2, 19): 117, (1, 2, 20): 119, (1, 2, 21): 111, (1, 2, 22): 103, (1, 2, 23): 102, (1, 2, 24): 104, (1, 2, 25): 126, (1, 2, 26): 128, (1, 2, 27): 127, (1, 2, 28): 125, (1, 2, 29): 128, (1, 2, 30): 117, (1, 2, 31): 117, (1, 2, 32): 57, (1, 2, 33): 59, (1, 2, 34): 58, (1, 2, 35): 60, (1, 2, 36): 83, (1, 2, 37): 84, (1, 2, 38): 81, (1, 2, 39): 83, (1, 2, 40): 84, (2, 1, 1): 45, (2, 1, 2): 32, (2, 1, 3): 32, (2, 1, 4): 31, (2, 1, 5): 30, (2, 1, 6): 61, (2, 1, 7): 63, (2, 1, 8): 61, (2, 1, 9): 62, (2, 1, 10): 63, (2, 1, 11): 64, (2, 1, 12): 54, (2, 1, 13): 55, (2, 1, 14): 54, (2, 1, 15): 51, (2, 1, 16): 52, (2, 1, 17): 50, (2, 1, 18): 50, (2, 1, 19): 57, (2, 1, 20): 57, (2, 1, 21): 54, (2, 1, 22): 50, (2, 1, 23): 49, (2, 1, 24): 50, (2, 1, 25): 62, (2, 1, 26): 62, (2, 1, 27): 63, (2, 1, 28): 63, (2, 1, 29): 64, (2, 1, 30): 58, (2, 1, 31): 57, (2, 1, 32): 30, (2, 1, 33): 31, (2, 1, 34): 30, (2, 1, 35): 32, (2, 1, 36): 41, (2, 1, 37): 42, (2, 1, 38): 42, (2, 1, 39): 43, (2, 1, 40): 41, (2, 2, 1): 91, (2, 2, 2): 58, (2, 2, 3): 57, (2, 2, 4): 57, (2, 2, 5): 57, (2, 2, 6): 121, (2, 2, 7): 121, (2, 2, 8): 121, (2, 2, 9): 124, (2, 2, 10): 121, (2, 2, 11): 123, (2, 2, 12): 106, (2, 2, 13): 106, (2, 2, 14): 105, (2, 2, 15): 100, (2, 2, 16): 99, (2, 2, 17): 100, (2, 2, 18): 100, (2, 2, 19): 114, (2, 2, 20): 116, (2, 2, 21): 106, (2, 2, 22): 98, (2, 2, 23): 100, (2, 2, 24): 99, (2, 2, 25): 121, (2, 2, 26): 121, (2, 2, 27): 122, (2, 2, 28): 122, (2, 2, 29): 124, (2, 2, 30): 116, (2, 2, 31): 116, (2, 2, 32): 58, (2, 2, 33): 58, (2, 2, 34): 59, (2, 2, 35): 58, (2, 2, 36): 77, (2, 2, 37): 80, (2, 2, 38): 80, (2, 2, 39): 79, (2, 2, 40): 80, (3, 1, 1): 35, (3, 1, 2): 21, (3, 1, 3): 21, (3, 1, 4): 22, (3, 1, 5): 23, (3, 1, 6): 50, (3, 1, 7): 50, (3, 1, 8): 52, (3, 1, 9): 51, (3, 1, 10): 50, (3, 1, 11): 52, (3, 1, 12): 43, (3, 1, 13): 44, (3, 1, 14): 42, (3, 1, 15): 39, (3, 1, 16): 38, (3, 1, 17): 38, (3, 1, 18): 39, (3, 1, 19): 46, (3, 1, 20): 47, (3, 1, 21): 44, (3, 1, 22): 39, (3, 1, 23): 38, (3, 1, 24): 39, (3, 1, 25): 52, (3, 1, 26): 49, (3, 1, 27): 49, (3, 1, 28): 50, (3, 1, 29): 50, (3, 1, 30): 46, (3, 1, 31): 48, (3, 1, 32): 23, (3, 1, 33): 21, (3, 1, 34): 22, (3, 1, 35): 21, (3, 1, 36): 31, (3, 1, 37): 29, (3, 1, 38): 31, (3, 1, 39): 29, (3, 1, 40): 30, (3, 2, 1): 90, (3, 2, 2): 57, (3, 2, 3): 58, (3, 2, 4): 60, (3, 2, 5): 58, (3, 2, 6): 126, (3, 2, 7): 126, (3, 2, 8): 125, (3, 2, 9): 127, (3, 2, 10): 128, (3, 2, 11): 128, (3, 2, 12): 111, (3, 2, 13): 110, (3, 2, 14): 110, (3, 2, 15): 103, (3, 2, 16): 103, (3, 2, 17): 104, (3, 2, 18): 103, (3, 2, 19): 114, (3, 2, 20): 114, (3, 2, 21): 110, (3, 2, 22): 104, (3, 2, 23): 102, (3, 2, 24): 103, (3, 2, 25): 128, (3, 2, 26): 125, (3, 2, 27): 125, (3, 2, 28): 126, (3, 2, 29): 127, (3, 2, 30): 115, (3, 2, 31): 113, (3, 2, 32): 59, (3, 2, 33): 57, (3, 2, 34): 58, (3, 2, 35): 59, (3, 2, 36): 81, (3, 2, 37): 82, (3, 2, 38): 83, (3, 2, 39): 83, (3, 2, 40): 81, (4, 1, 1): 39, (4, 1, 2): 24, (4, 1, 3): 23, (4, 1, 4): 22, (4, 1, 5): 21, (4, 1, 6): 52, (4, 1, 7): 49, (4, 1, 8): 51, (4, 1, 9): 52, (4, 1, 10): 50, (4, 1, 11): 50, (4, 1, 12): 47, (4, 1, 13): 48, (4, 1, 14): 47, (4, 1, 15): 43, (4, 1, 16): 42, (4, 1, 17): 44, (4, 1, 18): 43, (4, 1, 19): 45, (4, 1, 20): 47, (4, 1, 21): 45, (4, 1, 22): 43, (4, 1, 23): 41, (4, 1, 24): 43, (4, 1, 25): 51, (4, 1, 26): 52, (4, 1, 27): 52, (4, 1, 28): 52, (4, 1, 29): 49, (4, 1, 30): 47, (4, 1, 31): 47, (4, 1, 32): 21, (4, 1, 33): 23, (4, 1, 34): 23, (4, 1, 35): 22, (4, 1, 36): 34, (4, 1, 37): 36, (4, 1, 38): 35, (4, 1, 39): 33, (4, 1, 40): 34, (4, 2, 1): 89, (4, 2, 2): 58, (4, 2, 3): 57, (4, 2, 4): 57, (4, 2, 5): 59, (4, 2, 6): 127, (4, 2, 7): 128, (4, 2, 8): 125, (4, 2, 9): 127, (4, 2, 10): 125, (4, 2, 11): 125, (4, 2, 12): 105, (4, 2, 13): 108, (4, 2, 14): 107, (4, 2, 15): 102, (4, 2, 16): 104, (4, 2, 17): 104, (4, 2, 18): 102, (4, 2, 19): 114, (4, 2, 20): 114, (4, 2, 21): 105, (4, 2, 22): 104, (4, 2, 23): 104, (4, 2, 24): 104, (4, 2, 25): 126, (4, 2, 26): 126, (4, 2, 27): 125, (4, 2, 28): 125, (4, 2, 29): 125, (4, 2, 30): 114, (4, 2, 31): 114, (4, 2, 32): 57, (4, 2, 33): 60, (4, 2, 34): 58, (4, 2, 35): 58, (4, 2, 36): 81, (4, 2, 37): 82, (4, 2, 38): 84, (4, 2, 39): 84, (4, 2, 40): 81, (5, 1, 1): 33, (5, 1, 2): 24, (5, 1, 3): 23, (5, 1, 4): 23, (5, 1, 5): 23, (5, 1, 6): 48, (5, 1, 7): 46, (5, 1, 8): 48, (5, 1, 9): 48, (5, 1, 10): 48, (5, 1, 11): 46, (5, 1, 12): 41, (5, 1, 13): 41, (5, 1, 14): 44, (5, 1, 15): 38, (5, 1, 16): 40, (5, 1, 17): 39, (5, 1, 18): 38, (5, 1, 19): 41, (5, 1, 20): 43, (5, 1, 21): 43, (5, 1, 22): 40, (5, 1, 23): 39, (5, 1, 24): 37, (5, 1, 25): 46, (5, 1, 26): 48, (5, 1, 27): 47, (5, 1, 28): 48, (5, 1, 29): 46, (5, 1, 30): 42, (5, 1, 31): 44, (5, 1, 32): 22, (5, 1, 33): 23, (5, 1, 34): 21, (5, 1, 35): 23, (5, 1, 36): 32, (5, 1, 37): 32, (5, 1, 38): 29, (5, 1, 39): 32, (5, 1, 40): 30, (5, 2, 1): 91, (5, 2, 2): 63, (5, 2, 3): 64, (5, 2, 4): 63, (5, 2, 5): 62, (5, 2, 6): 126, (5, 2, 7): 127, (5, 2, 8): 128, (5, 2, 9): 125, (5, 2, 10): 125, (5, 2, 11): 127, (5, 2, 12): 111, (5, 2, 13): 112, (5, 2, 14): 111, (5, 2, 15): 102, (5, 2, 16): 102, (5, 2, 17): 103, (5, 2, 18): 104, (5, 2, 19): 120, (5, 2, 20): 120, (5, 2, 21): 112, (5, 2, 22): 103, (5, 2, 23): 101, (5, 2, 24): 104, (5, 2, 25): 127, (5, 2, 26): 125, (5, 2, 27): 127, (5, 2, 28): 127, (5, 2, 29): 127, (5, 2, 30): 119, (5, 2, 31): 118, (5, 2, 32): 64, (5, 2, 33): 61, (5, 2, 34): 63, (5, 2, 35): 64, (5, 2, 36): 83, (5, 2, 37): 84, (5, 2, 38): 83, (5, 2, 39): 83, (5, 2, 40): 82, (6, 1, 1): 33, (6, 1, 2): 21, (6, 1, 3): 22, (6, 1, 4): 21, (6, 1, 5): 22, (6, 1, 6): 47, (6, 1, 7): 48, (6, 1, 8): 47, (6, 1, 9): 45, (6, 1, 10): 46, (6, 1, 11): 45, (6, 1, 12): 37, (6, 1, 13): 39, (6, 1, 14): 40, (6, 1, 15): 38, (6, 1, 16): 37, (6, 1, 17): 39, (6, 1, 18): 38, (6, 1, 19): 43, (6, 1, 20): 42, (6, 1, 21): 39, (6, 1, 22): 40, (6, 1, 23): 38, (6, 1, 24): 39, (6, 1, 25): 47, (6, 1, 26): 45, (6, 1, 27): 48, (6, 1, 28): 46, (6, 1, 29): 45, (6, 1, 30): 44, (6, 1, 31): 41, (6, 1, 32): 21, (6, 1, 33): 21, (6, 1, 34): 23, (6, 1, 35): 21, (6, 1, 36): 30, (6, 1, 37): 32, (6, 1, 38): 32, (6, 1, 39): 31, (6, 1, 40): 30, (6, 2, 1): 90, (6, 2, 2): 64, (6, 2, 3): 62, (6, 2, 4): 63, (6, 2, 5): 64, (6, 2, 6): 127, (6, 2, 7): 127, (6, 2, 8): 126, (6, 2, 9): 125, (6, 2, 10): 128, (6, 2, 11): 126, (6, 2, 12): 109, (6, 2, 13): 111, (6, 2, 14): 111, (6, 2, 15): 103, (6, 2, 16): 103, (6, 2, 17): 102, (6, 2, 18): 103, (6, 2, 19): 120, (6, 2, 20): 120, (6, 2, 21): 110, (6, 2, 22): 102, (6, 2, 23): 101, (6, 2, 24): 102, (6, 2, 25): 126, (6, 2, 26): 128, (6, 2, 27): 127, (6, 2, 28): 128, (6, 2, 29): 127, (6, 2, 30): 120, (6, 2, 31): 117, (6, 2, 32): 64, (6, 2, 33): 63, (6, 2, 34): 62, (6, 2, 35): 62, (6, 2, 36): 82, (6, 2, 37): 82, (6, 2, 38): 82, (6, 2, 39): 84, (6, 2, 40): 84, (7, 1, 1): 79, (7, 1, 2): 50, (7, 1, 3): 50, (7, 1, 4): 49, (7, 1, 5): 50, (7, 1, 6): 108, (7, 1, 7): 105, (7, 1, 8): 108, (7, 1, 9): 106, (7, 1, 10): 107, (7, 1, 11): 106, (7, 1, 12): 89, (7, 1, 13): 89, (7, 1, 14): 90, (7, 1, 15): 88, (7, 1, 16): 85, (7, 1, 17): 86, (7, 1, 18): 86, (7, 1, 19): 100, (7, 1, 20): 98, (7, 1, 21): 89, (7, 1, 22): 87, (7, 1, 23): 87, (7, 1, 24): 85, (7, 1, 25): 107, (7, 1, 26): 105, (7, 1, 27): 107, (7, 1, 28): 108, (7, 1, 29): 105, (7, 1, 30): 98, (7, 1, 31): 98, (7, 1, 32): 49, (7, 1, 33): 50, (7, 1, 34): 51, (7, 1, 35): 50, (7, 1, 36): 71, (7, 1, 37): 72, (7, 1, 38): 69, (7, 1, 39): 72, (7, 1, 40): 70, (7, 2, 1): 48, (7, 2, 2): 29, (7, 2, 3): 31, (7, 2, 4): 32, (7, 2, 5): 30, (7, 2, 6): 61, (7, 2, 7): 63, (7, 2, 8): 64, (7, 2, 9): 64, (7, 2, 10): 64, (7, 2, 11): 61, (7, 2, 12): 55, (7, 2, 13): 53, (7, 2, 14): 56, (7, 2, 15): 49, (7, 2, 16): 49, (7, 2, 17): 50, (7, 2, 18): 51, (7, 2, 19): 57, (7, 2, 20): 57, (7, 2, 21): 55, (7, 2, 22): 50, (7, 2, 23): 49, (7, 2, 24): 51, (7, 2, 25): 61, (7, 2, 26): 61, (7, 2, 27): 64, (7, 2, 28): 61, (7, 2, 29): 61, (7, 2, 30): 59, (7, 2, 31): 58, (7, 2, 32): 32, (7, 2, 33): 29, (7, 2, 34): 31, (7, 2, 35): 32, (7, 2, 36): 44, (7, 2, 37): 44, (7, 2, 38): 42, (7, 2, 39): 43, (7, 2, 40): 41, (8, 1, 1): 73, (8, 1, 2): 50, (8, 1, 3): 49, (8, 1, 4): 49, (8, 1, 5): 49, (8, 1, 6): 101, (8, 1, 7): 104, (8, 1, 8): 102, (8, 1, 9): 102, (8, 1, 10): 101, (8, 1, 11): 104, (8, 1, 12): 89, (8, 1, 13): 92, (8, 1, 14): 89, (8, 1, 15): 84, (8, 1, 16): 82, (8, 1, 17): 84, (8, 1, 18): 84, (8, 1, 19): 94, (8, 1, 20): 96, (8, 1, 21): 89, (8, 1, 22): 83, (8, 1, 23): 82, (8, 1, 24): 83, (8, 1, 25): 101, (8, 1, 26): 103, (8, 1, 27): 103, (8, 1, 28): 103, (8, 1, 29): 102, (8, 1, 30): 96, (8, 1, 31): 94, (8, 1, 32): 51, (8, 1, 33): 49, (8, 1, 34): 51, (8, 1, 35): 51, (8, 1, 36): 67, (8, 1, 37): 66, (8, 1, 38): 66, (8, 1, 39): 68, (8, 1, 40): 67, (8, 2, 1): 48, (8, 2, 2): 30, (8, 2, 3): 30, (8, 2, 4): 30, (8, 2, 5): 31, (8, 2, 6): 66, (8, 2, 7): 68, (8, 2, 8): 67, (8, 2, 9): 68, (8, 2, 10): 66, (8, 2, 11): 67, (8, 2, 12): 57, (8, 2, 13): 57, (8, 2, 14): 57, (8, 2, 15): 53, (8, 2, 16): 56, (8, 2, 17): 54, (8, 2, 18): 54, (8, 2, 19): 64, (8, 2, 20): 62, (8, 2, 21): 60, (8, 2, 22): 54, (8, 2, 23): 54, (8, 2, 24): 54, (8, 2, 25): 65, (8, 2, 26): 65, (8, 2, 27): 67, (8, 2, 28): 65, (8, 2, 29): 66, (8, 2, 30): 62, (8, 2, 31): 63, (8, 2, 32): 30, (8, 2, 33): 29, (8, 2, 34): 31, (8, 2, 35): 31, (8, 2, 36): 44, (8, 2, 37): 42, (8, 2, 38): 41, (8, 2, 39): 43, (8, 2, 40): 41, (9, 1, 1): 72, (9, 1, 2): 48, (9, 1, 3): 47, (9, 1, 4): 47, (9, 1, 5): 47, (9, 1, 6): 103, (9, 1, 7): 102, (9, 1, 8): 102, (9, 1, 9): 102, (9, 1, 10): 104, (9, 1, 11): 104, (9, 1, 12): 86, (9, 1, 13): 86, (9, 1, 14): 86, (9, 1, 15): 83, (9, 1, 16): 83, (9, 1, 17): 84, (9, 1, 18): 84, (9, 1, 19): 96, (9, 1, 20): 93, (9, 1, 21): 87, (9, 1, 22): 81, (9, 1, 23): 81, (9, 1, 24): 82, (9, 1, 25): 101, (9, 1, 26): 102, (9, 1, 27): 102, (9, 1, 28): 104, (9, 1, 29): 104, (9, 1, 30): 96, (9, 1, 31): 94, (9, 1, 32): 46, (9, 1, 33): 47, (9, 1, 34): 46, (9, 1, 35): 47, (9, 1, 36): 68, (9, 1, 37): 67, (9, 1, 38): 66, (9, 1, 39): 66, (9, 1, 40): 65, (9, 2, 1): 51, (9, 2, 2): 29, (9, 2, 3): 29, (9, 2, 4): 32, (9, 2, 5): 32, (9, 2, 6): 72, (9, 2, 7): 70, (9, 2, 8): 69, (9, 2, 9): 70, (9, 2, 10): 72, (9, 2, 11): 71, (9, 2, 12): 57, (9, 2, 13): 57, (9, 2, 14): 58, (9, 2, 15): 54, (9, 2, 16): 53, (9, 2, 17): 54, (9, 2, 18): 56, (9, 2, 19): 61, (9, 2, 20): 62, (9, 2, 21): 59, (9, 2, 22): 53, (9, 2, 23): 55, (9, 2, 24): 54, (9, 2, 25): 72, (9, 2, 26): 69, (9, 2, 27): 71, (9, 2, 28): 70, (9, 2, 29): 71, (9, 2, 30): 64, (9, 2, 31): 64, (9, 2, 32): 32, (9, 2, 33): 30, (9, 2, 34): 29, (9, 2, 35): 31, (9, 2, 36): 43, (9, 2, 37): 42, (9, 2, 38): 43, (9, 2, 39): 44, (9, 2, 40): 44, (10, 1, 1): 83, (10, 1, 2): 56, (10, 1, 3): 55, (10, 1, 4): 53, (10, 1, 5): 56, (10, 1, 6): 119, (10, 1, 7): 117, (10, 1, 8): 120, (10, 1, 9): 120, (10, 1, 10): 119, (10, 1, 11): 119, (10, 1, 12): 104, (10, 1, 13): 102, (10, 1, 14): 103, (10, 1, 15): 93, (10, 1, 16): 95, (10, 1, 17): 93, (10, 1, 18): 96, (10, 1, 19): 107, (10, 1, 20): 105, (10, 1, 21): 103, (10, 1, 22): 95, (10, 1, 23): 93, (10, 1, 24): 93, (10, 1, 25): 118, (10, 1, 26): 117, (10, 1, 27): 117, (10, 1, 28): 120, (10, 1, 29): 117, (10, 1, 30): 106, (10, 1, 31): 108, (10, 1, 32): 54, (10, 1, 33): 54, (10, 1, 34): 55, (10, 1, 35): 56, (10, 1, 36): 73, (10, 1, 37): 76, (10, 1, 38): 75, (10, 1, 39): 73, (10, 1, 40): 73, (10, 2, 1): 41, (10, 2, 2): 27, (10, 2, 3): 25, (10, 2, 4): 28, (10, 2, 5): 25, (10, 2, 6): 60, (10, 2, 7): 59, (10, 2, 8): 57, (10, 2, 9): 60, (10, 2, 10): 59, (10, 2, 11): 58, (10, 2, 12): 50, (10, 2, 13): 52, (10, 2, 14): 52, (10, 2, 15): 48, (10, 2, 16): 45, (10, 2, 17): 48, (10, 2, 18): 46, (10, 2, 19): 55, (10, 2, 20): 54, (10, 2, 21): 49, (10, 2, 22): 47, (10, 2, 23): 45, (10, 2, 24): 48, (10, 2, 25): 57, (10, 2, 26): 57, (10, 2, 27): 60, (10, 2, 28): 59, (10, 2, 29): 59, (10, 2, 30): 55, (10, 2, 31): 53, (10, 2, 32): 27, (10, 2, 33): 27, (10, 2, 34): 26, (10, 2, 35): 27, (10, 2, 36): 40, (10, 2, 37): 37, (10, 2, 38): 37, (10, 2, 39): 39, (10, 2, 40): 37}
    
    perturbed_travel_time_by_rail = perturb_travel_time(travel_time_by_rail)
    perturbed_travel_time_by_ship_to_spoe = perturb_travel_time(travel_time_by_ship_to_spoe)
    perturbed_travel_time_by_ship_to_spod = perturb_travel_time(travel_time_by_ship_to_spod)
    return (perturbed_travel_time_by_rail, perturbed_travel_time_by_ship_to_spoe, perturbed_travel_time_by_ship_to_spod)

def kwag_generator(all_scenario_names):
    travel_times = {}
    for key in all_scenario_names:
        travel_time_by_rail = generate_rail_travel_times(2)
        ship_travel_times = generate_ship_travel_times(2, 15)
        travel_times_single = {
                **travel_time_by_rail, 
                **ship_travel_times}
        travel_times[key] = travel_times_single 
    return {'all_travel_times': travel_times}

def generate_scenario_names(n):
    return [f"scenario{str(i).zfill(3)}" for i in range(1, n + 1)]
# n = int(input("Enter the number of scenario names to generate: "))

def scenario_creator(scenario_name, all_travel_times):
    travel_times = all_travel_times[scenario_name]
    model = build_model(travel_times)
    # Attach the root node and set probability
    sputils.attach_root_node(model, model.FirstStageCost, [model.y_open])
    model._mpisppy_probability = 1.0/ len(all_travel_times) 
    return model




def scenario_denouement(rank, scenario_name, scenario):
    pass

from mpisppy.opt.lshaped import LShapedMethod
from mpisppy.opt.ph import PH
def main():
    


    # num_Scenarios = int(input("Number of scenarios:"))
    # num_iterations = int(input("Number of iterations:" ))
    num_Scenarios = 5
    #1732.91 at 10
    
    num_iterations = 150
    all_scenario_names = generate_scenario_names(num_Scenarios)
    # cfg = config.Config()
    # cfg.popular_args()
    # cfg.fwph_args()
    # cfg.xhatlshaped_args()
    # # cfg.num_scens_required()
    # cfg.popular_args()
    # cfg.two_sided_args()
    # cfg.add_and_assign("solver_name",
    #     description= "solver name (default None)",
    #     domain = str,
    #     default=None,
    #     value = "gurobi_persistent")
    # cfg.parse_command_line()
    # # cfg.lagrangian_iter0_mipgap
    # # cfg.lagrangian_iterk_mipgap
    # # cfg.add_to_config(f"{sstr}_options",
    # #                         description= "solver options; space delimited with = for values (default None)",
    # #                         domain = str,
    # #                         default=None)




    bounds = {name: -432000 for name in all_scenario_names}
    options = {
        "root_solver": "gurobi_persistent",
        "sp_solver": "gurobi_persistent",
        "sp_solver_options" : {"threads" : 1},
        "valid_eta_lb": bounds,
        "max_iter": num_iterations,
        #"tol": 1e5, 
        "verbose": True
    }

    # cfg.solver_name = "gurobi_persistent"

    ls = LShapedMethod(
        options,
        all_scenario_names,
        scenario_creator,
        scenario_creator_kwargs=kwag_generator(all_scenario_names))
    result = ls.lshaped_algorithm()

    variables = ls.gather_var_values_to_rank0()
    for ((scen_name, var_name), var_value) in variables.items():
        print(scen_name, var_name, var_value)



    # options = {
    #     "solver_name": "gurobi_persistent",
    #     "PHIterLimit": 5,
    #     "defaultPHrho": 0.1,
    #     "convthresh": 1e7,
    #     "verbose": False,
    #     "display_progress": False,
    #     "display_timing": False,
    #     "iter0_solver_options": dict(),
    #     "iterk_solver_options": dict(),
    # }
    # ph = PH(
    #     options,
    #     all_scenario_names,
    #     scenario_creator,
    #     scenario_creator_kwargs=kwag_generator(all_scenario_names)
    # )
    # ph.ph_main()




if __name__ == "__main__":
    main()
