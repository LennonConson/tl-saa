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
            ( 9, 9): 0,    ( 9, 10): 199,  ( 9, 11): 219,  ( 9, 12): 429,  ( 9, 13): 4904,   # Charleston
            (10, 9): 199,  (10, 10): 0,    (10, 11): 376,  (10, 12): 592,  (10, 13): 4904,   # Jacksonville
            (11, 9): 219,  (11, 10): 376,  (11, 11): 0,    (11, 12): 254,  (11, 13): 3678,   # Morehead City
            (12, 9): 429,  (12, 10): 592,  (12, 11): 254,  (12, 12): 0,    (12, 13): 3678,   # Portsmouth
            ( 0, 9): 0,    ( 0, 10): 0,    ( 0, 11): 0,    ( 0, 12): 0,    ( 0, 13): 0}      # Open
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



