import random
import numpy as np
def generate_rail_travel_times(divisions_per_day):
    travel_time_by_rail = {
                           ( 1, 1): 5,  ( 1, 2): 5,  ( 1, 3): 7,  ( 1, 4): 6,  ( 1, 5): 8,  ( 1, 6): 6,  # Camp Atterbury                                                      
                           ( 2, 1): 7,  ( 2, 2): 8,  ( 2, 3): 4,  ( 2, 4): 2,  ( 2, 5): 4,  ( 2, 6): 6,  # Fort Stewart
                           ( 3, 1): 11, ( 3, 2): 8,  ( 3, 3): 1,  ( 3, 4): 2,  ( 3, 5): 4,  ( 3, 6): 1,  # Fort Bragg
                           ( 4, 1): 10, ( 4, 2): 8,  ( 4, 3): 1,  ( 4, 4): 7,  ( 4, 5): 4,  ( 4, 6): 4,  # Camp Lejeune
                           ( 5, 1): 7,  ( 5, 2): 6,  ( 5, 3): 8,  ( 5, 4): 8,  ( 5, 5): 8,  ( 5, 6): 5,  # Fort Campbell
                           ( 6, 1): 14, ( 6, 2): 11, ( 6, 3): 5,  ( 6, 4): 9,  ( 6, 5): 7,  ( 6, 6): 6,  # Fort Drum
                           ( 7, 1): 12, ( 7, 2): 11, ( 7, 3): 8,  ( 7, 4): 6,  ( 7, 5): 6,  ( 7, 6): 1,  # Fort Dix
                           ( 8, 1): 2,  ( 8, 2): 3,  ( 8, 3): 10, ( 8, 4): 8,  ( 8, 5): 11, ( 8, 6): 10, # Fort Polk
                           ( 9, 1): 8,  ( 9, 2): 7,  ( 9, 3): 5,  ( 9, 4): 7,  ( 9, 5): 5,  ( 9, 6): 6,  # Fort Knox
                           (10, 1): 4,  (10, 2): 3,  (10, 3): 7,  (10, 4): 7,  (10, 5): 8,  (10, 6): 8}  # Camp Shelby
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
        rail_travel_times[(A, B+10, 0)] = max(round(np.random.lognormal(mean=mu, sigma=sigma)),1)
    return rail_travel_times
