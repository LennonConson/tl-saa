import numpy as np
        # List of ships
        # 7 x Bob Hope 44 km/h, 35,000 m2
        # 1 through 7
        ## Tacoma(10) x 3
        ## Jacksonville(4) x 2
        ## Norfolk(6), USAx2
        
        # 7 x Watson 44 km/h, 36,511 m2
        # 8 through 14
        ## Baltimore(6) x 3
        ## Charleston(3) x 1
        ## Norfolk(6) x 3
        
        # 2 x Gordon Class 44 km/h 26,390.4 m2
        # 15,16
        ## 2x Baltimore(6)
        
        # 2 x Shughart Class 44 km/h 29,029 m2
        # 17,18
        ## NORFOLK(6)x2
def generate_ship_travel_times(divisions_per_day, num_V):

    distance_table_nm = {
        (16, 16): 0,      (16, 17): 408,    (16, 18): 1336, (16, 19): 1226, (16, 20): 1475, (16, 21): 1662, (16, 22): 5210.5,
        (17, 16): 408,    (17, 17): 0,      (17, 18): 1120, (17, 19): 1014, (17, 20): 1261, (17, 21): 1449, (17, 22): 4904,
        (18, 16): 1336,   (18, 17): 1120,   (18, 18): 0,    (18, 19): 199,  (18, 20): 219,  (18, 21): 429,  (18, 22): 4904,
        (19, 16): 1226,   (19, 17): 1014,   (19, 18): 199,  (19, 19): 0,    (19, 20): 376,  (19, 21): 592,  (19, 22): 4904,
        (20, 16): 1475,   (20, 17): 1261,   (20, 18): 219,  (20, 19): 376,  (20, 20): 0,    (20, 21): 254,  (20, 22): 3678,
        (21, 16): 1662,   (21, 17): 1449,   (21, 18): 429,  (21, 19): 592,  (21, 20): 254,  (21, 21): 0,    (21, 22): 3678,
        ( 0, 16): 0,       (0, 17): 0,       (0, 18): 0,     (0, 19): 0,     (0, 20): 0,     (0, 21): 0,    ( 0, 22): 0}
    NAUTICAL_MILE_TO_KM = 1.852
    distance_table_km = { pair: round(nm * NAUTICAL_MILE_TO_KM, 2) for pair, nm in distance_table_nm.items()}

    vehicle_speeds = 44 # km/h (max speed)
    vehicle_speeds_effective = vehicle_speeds* (24/divisions_per_day) # convert to current timeperiods
    # Assumptions
    m = 0.1                   # Mean travel experiances a 10% delay
    CV = 0.2                    # 20% variability

    ship_travel_times = {}

    for (A, B), distance in distance_table_km.items():
        for v in range(1,num_V+1):
            if distance == 0:
                ship_travel_times[(A, B, v)] = 0
            else:
                t_min = distance / vehicle_speeds_effective 
                mean_travel_time = t_min * (1 + m) # minimum possible time (ideal conditions)
                sigma = np.sqrt(np.log(CV**2 + 1))
                mu = np.log(mean_travel_time) - (sigma**2 / 2)
                ship_travel_times[(A, B, v)] = max(round(np.random.lognormal(mean=mu, sigma=sigma)),1)
    return ship_travel_times



