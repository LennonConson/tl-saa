import random

import numpy as np
from scipy.stats import lognorm

def generate_rail_travel_times(divisions_per_day, percentile_delays, average_delay=0.15, sigma=1.0):
    travel_time_by_rail = { ( 1, 1): 7,  ( 1, 2): 8,  ( 1, 3): 4,  ( 1, 4): 2,  ( 1, 5): 4,  ( 1, 6): 6,    # Fort Stewart
                            ( 2, 1): 11, ( 2, 2): 8,  ( 2, 3): 1,  ( 2, 4): 2,  ( 2, 5): 4,  ( 2, 6): 1,    # Fort Bragg
                            ( 3, 1): 10, ( 3, 2): 8,  ( 3, 3): 1,  ( 3, 4): 7,  ( 3, 5): 4,  ( 3, 6): 4,    # Camp Lejeune
                            ( 4, 1): 2,  ( 4, 2): 3,  ( 4, 3): 10, ( 4, 4): 8,  ( 4, 5): 11, ( 4, 6): 10,   # Fort Polk
                            ( 5, 1): 4,  ( 5, 2): 3,  ( 5, 3): 7,  ( 5, 4): 7,  ( 5, 5): 8,  ( 5, 6): 8,  } # Camp Shelby

    # # Assuming the above travel times have been rounded to the nearest hour
    # # we try to reintroduce non-integer travel times by adding a small random value
    # travel_time_by_rail_hours = {
    #     key: 24*(value + random.uniform(-0.5, 0.4999999999999999))
    #     for key, value in travel_time_by_rail.items()
    # }
    # print(travel_time_by_rail_hours)
    travel_time_by_rail_hours = {(1, 1): 171.3462431629892, (1, 2): 180.600258125344, (1, 3): 90.60070364085885, (1, 4): 41.35705771557175, (1, 5): 101.6753091399363, (1, 6): 148.24078769814986, (2, 1): 273.4123096249163, (2, 2): 182.086531983106, (2, 3): 22.12612367244649, (2, 4): 36.71513326651369, (2, 5): 89.24731139528649, (2, 6): 24.128526914480695, (3, 1): 228.6368632724127, (3, 2): 184.77210361647957, (3, 3): 27.59722650670855, (3, 4): 169.0785955344772, (3, 5): 89.29057492897672, (3, 6): 98.14237641302182, (4, 1): 55.42633096026783, (4, 2): 60.15597023227346, (4, 3): 247.3396620439874, (4, 4): 196.75534547971745, (4, 5): 260.1660123964318, (4, 6): 231.73150799548273, (5, 1): 106.97311373296276, (5, 2): 68.07826908270305, (5, 3): 158.22590024112355, (5, 4): 158.32119304400314, (5, 5): 200.33986479233903, (5, 6): 194.4894247528054}

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

# Example usage:
if __name__ == "__main__":
    divisions_per_day = 24
    percentile_delays = {i: 0.5 for i in range(1, 13)}  # dummy percentiles
    generate_rail_travel_times(divisions_per_day, percentile_delays)
