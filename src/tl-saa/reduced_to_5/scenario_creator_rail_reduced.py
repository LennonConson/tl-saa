import random
import numpy as np
def generate_rail_travel_times(divisions_per_day):
    travel_time_by_rail = {                        
        ( 1, 2):  5, ( 1, 3):  7, ( 1, 4): 6, ( 1, 5): 8, ( 1, 6): 6, # Camp Atterbury                                                
        ( 2, 2):  8, ( 2, 3):  4, ( 2, 4): 2, ( 2, 5): 4, ( 2, 6): 6, # Fort Stewart
        ( 3, 2):  8, ( 3, 3):  1, ( 3, 4): 2, ( 3, 5): 4, ( 3, 6): 1, # Fort Bragg
        ( 4, 2):  9, ( 4, 3): 11, ( 4, 4): 11, (4, 5): 9, ( 4, 6): 9, # Fort McCoy                        
        ( 5, 2):  8, ( 5, 3):  1, ( 5, 4): 7, ( 5, 5): 4, ( 5, 6): 4, # Camp Lejeune
        ( 6, 2):  6, ( 6, 3):  8, ( 6, 4): 8, ( 6, 5): 8, ( 6, 6): 5, # Fort Campbell                     
        ( 7, 2): 11, ( 7, 3):  5, ( 7, 4): 9, ( 7, 5): 7, ( 7, 6): 6, # Fort Drum
        ( 8, 2): 11, ( 8, 3):  8, ( 8, 4): 6, ( 8, 5): 6, ( 8, 6): 1, # Fort Dix
        ( 9, 2):  7, ( 9, 3):  5, ( 9, 4): 7, ( 9, 5): 5, ( 9, 6): 6, # Fort Knox
        (10, 2):  3, (10, 3):  7, (10, 4): 7, (10, 5): 8, (10, 6): 8} # Camp Shelby

    # 1 → X Fort Hood
    # 2 → X Fort Lewis
    # 3 → 1 Camp Atterbury
    # 4 → X Fort Bliss
    # 5 → X Camp Pendleton
    # 6 → 2 Fort Stewart
    # 7 → 3 Fort Bragg
    # 8 → 4 Fort McCoy
    # 9 → X Fort Carson
    # 10 → 5 Camp Lejeune
    # 11 → 6 Fort Campbell
    # 12 → X Fort Riley
    # 13 → 7 Fort Drum
    # 14 → 8 Fort Dix
    # 15 → X Fort Polk
    # 16 → X Fort Sill
    # 17 → X Fort Irwin
    # 18 → 9 Fort Knox
    # 19 → X Fort Leonard Wood
    # 20 → 10 Camp Shelby

    # 21 → X
    # 22 → 11
    # 23 → 12
    # 24 → 13
    # 25 → 14
    # 26 → 15
    # 27 → X
    # 28 → X
    # 29 → X
    # 30 → X
    # 31 → 16

    travel_time_by_rail = {
        key: value + random.uniform(-0.5, 0.4999999999999999)
        for key, value in travel_time_by_rail.items()
    }



    interval_adj_travel_time_by_rail = {
        key: round(value * divisions_per_day)
        for key, value in travel_time_by_rail.items()
    }

    # Assumptions
    CV = 0.2                   # 20% variability
    rail_travel_times = {}

    for (A, B), mean_travel_time in interval_adj_travel_time_by_rail.items():
        sigma = np.sqrt(np.log(CV**2 + 1))
        mu = np.log(mean_travel_time) - (sigma**2 / 2)
        rail_travel_times[(A, B+15, 0)] = max(round(np.random.lognormal(mean=mu, sigma=sigma)),1)
    return rail_travel_times
