import random
import numpy as np
def generate_rail_travel_times(divisions_per_day):
    travel_time_by_rail = {
                           ( 1, 1): 7,  ( 1, 2): 6,  ( 1, 3): 8,  ( 1, 4): 6,  # Camp Atterbury                                                      
                           ( 2, 1): 4,  ( 2, 2): 2,  ( 2, 3): 4,  ( 2, 4): 6,  # Fort Stewart
                           ( 3, 1): 1,  ( 3, 2): 2,  ( 3, 3): 4,  ( 3, 4): 1,  # Fort Bragg
                           ( 4, 1): 1,  ( 4, 2): 7,  ( 4, 3): 4,  ( 4, 4): 4,  # Camp Lejeune
                           ( 5, 1): 8,  ( 5, 2): 8,  ( 5, 3): 8,  ( 5, 4): 5,  # Fort Campbell
                           ( 6, 1): 5,  ( 6, 2): 9,  ( 6, 3): 7,  ( 6, 4): 6,  # Fort Drum
                           ( 7, 1): 8,  ( 7, 2): 6,  ( 7, 3): 6,  ( 7, 4): 1,  # Fort Dix
                           ( 8, 1): 5,  ( 8, 2): 7,  ( 8, 3): 5,  ( 8, 4): 6}  # Fort Knox
                           
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
        rail_travel_times[(A, B+8, 0)] = max(round(np.random.lognormal(mean=mu, sigma=sigma)),1)
    return rail_travel_times
