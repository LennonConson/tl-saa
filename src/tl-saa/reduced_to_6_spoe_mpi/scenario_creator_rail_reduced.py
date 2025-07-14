import random
import numpy as np
from scipy.stats import lognorm

def generate_rail_travel_times(divisions_per_day, percentile_delays, average_delay=0.15, sigma=1.0):
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
    # Assuming the above travel times have been rounded to the nearest hour
    # we try to reintroduce non-integer travel times by adding a small random value
    travel_time_by_rail_hours = {
        key: 24*(value + random.uniform(-0.5, 0.4999999999999999))
        for key, value in travel_time_by_rail.items()
    }
    origins = {key[0] for key in travel_time_by_rail.keys()}
    


    perturbed_time_to_reach_destination = {}
    for (A, B), time_days in travel_time_by_rail_hours.items():
        b_adj = B + max(origins)
        scale = average_delay * time_days
        log_normal_adjustment = lognorm.ppf(percentile_delays[b_adj], s=sigma, loc=0, scale=scale)
        perturbed_time_to_reach_destination[(A, b_adj, 0)] = time_days + log_normal_adjustment
    
    
    CONVERT_TIME = divisions_per_day/24 # convert to current timeperiods

    rail_travel_times = {k: round(v * CONVERT_TIME) for k, v in perturbed_time_to_reach_destination.items()}

    return rail_travel_times
