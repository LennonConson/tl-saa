import random
import numpy as np
def generate_rail_travel_times(divisions_per_day):
    travel_time_by_rail = {(1, 1): 1,   (1, 2): 8,   (1, 3): 12,  (1, 4): 11,  (1, 5): 12,  (1, 6): 15, 
                           (2, 1): 5,   (2, 2): 5,   (2, 3): 7,   (2, 4): 6,   (2, 5): 8,   (2, 6): 6,
                           (3, 1): 7,   (3, 2): 8,   (3, 3): 4,   (3, 4): 2,   (3, 5): 4,   (3, 6): 6,
                           (4, 1): 11,  (4, 2): 8,   (4, 3): 1,   (4, 4): 2,   (4, 5): 4,   (4, 6): 1,
                           (5, 1): 9,   (5, 2): 9,   (5, 3): 11,  (5, 4): 11,  (5, 5): 9,   (5, 6): 9,
                           (6, 1): 10,  (6, 2): 8,   (6, 3): 1,   (6, 4): 7,   (6, 5): 4,   (6, 6): 4,
                           (7, 1): 7,   (7, 2): 6,   (7, 3): 8,   (7, 4): 8,   (7, 5): 8,   (7, 6): 5,
                           (8, 1): 8,   (8, 2): 5,   (8, 3): 9,   (8, 4): 11,  (8, 5): 10,  (8, 6): 10,
                           (9, 1): 14,  (9, 2): 11,  (9, 3): 5,   (9, 4): 9,   (9, 5): 7,   (9, 6): 6,
                           (10, 1): 12, (10, 2): 11, (10, 3): 8,  (10, 4): 6,  (10, 5): 6,  (10, 6): 1,
                           (11, 1): 2,  (11, 2): 3,  (11, 3): 10, (11, 4): 8,  (11, 5): 11, (11, 6): 10,
                           (12, 1): 5,  (12, 2): 8,  (12, 3): 10, (12, 4): 12, (12, 5): 16, (12, 6): 15,
                           (13, 1): 8,  (13, 2): 7,  (13, 3): 5,  (13, 4): 7,  (13, 5): 5,  (13, 6): 6,
                           (14, 1): 6,  (14, 2): 5,  (14, 3): 11, (14, 4): 12, (14, 5): 12, (14, 6): 11,
                           (15, 1): 4,  (15, 2): 3,  (15, 3): 7,  (15, 4): 7,  (15, 5): 8,  (15, 6): 8}

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
