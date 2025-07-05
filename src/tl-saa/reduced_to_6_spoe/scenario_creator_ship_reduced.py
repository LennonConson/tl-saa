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
            (11, 11): 0,      (11, 12): 408,    (11, 13): 1336, (11, 14): 1226, (11, 15): 1475, (11, 16): 1662, (11, 17): 5210.5, # Beaumont
            (12, 11): 408,    (12, 12): 0,      (12, 13): 1120, (12, 14): 1014, (12, 15): 1261, (12, 16): 1449, (12, 17): 4904,   # Gulfport
            (13, 11): 1336,   (13, 12): 1120,   (13, 13): 0,    (13, 14): 199,  (13, 15): 219,  (13, 16): 429,  (13, 17): 4904,   # Charleston
            (14, 11): 1226,   (14, 12): 1014,   (14, 13): 199,  (14, 14): 0,    (14, 15): 376,  (14, 16): 592,  (14, 17): 4904,   # Jacksonville
            (15, 11): 1475,   (15, 12): 1261,   (15, 13): 219,  (15, 14): 376,  (15, 15): 0,    (15, 16): 254,  (15, 17): 3678,   # Morehead City
            (16, 11): 1662,   (16, 12): 1449,   (16, 13): 429,  (16, 14): 592,  (16, 15): 254,  (16, 16): 0,    (16, 17): 3678,   # Portsmouth
            ( 0, 11): 0,      ( 0, 12): 0,      ( 0, 13): 0,    ( 0, 14): 0,    ( 0, 15): 0,    ( 0, 16): 0,    ( 0, 17): 0}      # Open
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



