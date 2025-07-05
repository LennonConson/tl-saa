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
    divisions_per_day = 2
    num_V = 18

    distance_table_nm = {
            (21, 21): 0,      (21, 22): 408,    (21, 23): 1336, (21, 24): 1226, (21, 25): 1475, (21, 26): 1662, (21, 27): 4791,   (21, 28): 4457,   (21, 29): 4389, (21, 30): 5570,   (21, 31): 5210.5, #Beaumont
            (22, 21): 408,    (22, 22): 0,      (22, 23): 1120, (22, 24): 1014, (22, 25): 1261, (22, 26): 1449, (22, 27): 4644,   (22, 28): 4310,   (22, 29): 4242, (22, 30): 5423,   (22, 31): 4904,   # Gulfport
            (23, 21): 1336,   (23, 22): 1120,   (23, 23): 0,    (23, 24): 199,  (23, 25): 219,  (23, 26): 429,  (23, 27): 4845,   (23, 28): 4511,   (23, 29): 4443, (23, 30): 5624,   (23, 31): 4904,   # Charleston
            (24, 21): 1226,   (24, 22): 1014,   (24, 23): 199,  (24, 24): 0,    (24, 25): 376,  (24, 26): 592,  (24, 27): 4790,   (24, 28): 4456,   (24, 29): 4388, (24, 30): 5569,   (24, 31): 4904,   # Jacksonville
            (25, 21): 1475,   (25, 22): 1261,   (25, 23): 219,  (25, 24): 376,  (25, 25): 0,    (25, 26): 254,  (25, 27): 4909,   (25, 28): 4575,   (25, 29): 4507, (25, 30): 5688,   (25, 31): 3678,   # Morehead City
            (26, 21): 1662,   (26, 22): 1449,   (26, 23): 429,  (26, 24): 592,  (26, 25): 254,  (26, 26): 0,    (26, 27): 5066,   (26, 28): 4732,   (26, 29): 4664, (26, 30): 5845,   (26, 31): 3678,   # Portsmouth
            (27, 21): 4791,   (27, 22): 4644,   (27, 23): 4845, (27, 24): 4790, (27, 25): 4909, (27, 26): 5066, (27, 27): 0,      (27, 28): 369,    (27, 29): 453,  (27, 30): 816,    (27, 31): 8275.5, # Oakland
            (28, 21): 4457,   (28, 22): 4310,   (28, 23): 4511, (28, 24): 4456, (28, 25): 4575, (28, 26): 4732, (28, 27): 369,    (28, 28): 0,      (28, 29): 95,   (28, 30): 1165,   (28, 31): 7969,   # Port Hueneme
            (29, 21): 4389,   (29, 22): 4242,   (29, 23): 4443, (29, 24): 4388, (29, 25): 4507, (29, 26): 4664, (29, 27): 453,    (29, 28): 95,     (29, 29): 0,    (29, 30): 1229,   (29, 31): 7969,   # San Diego
            (30, 21): 5570,   (30, 22): 5423,   (30, 23): 5624, (30, 24): 5569, (30, 25): 5688, (30, 26): 5845, (30, 27): 816,    (30, 28): 1165,   (30, 29): 1229, (30, 30): 0,      (30, 31): 9195,   # Tacoma
            ( 0, 21): 0,      ( 0, 22): 0,      ( 0, 23): 0,    ( 0, 24): 0,    ( 0, 25): 0,    ( 0, 26): 0,    ( 0, 27): 0,      ( 0, 28): 0,      ( 0, 29): 0,    ( 0, 30): 0,      ( 0, 31): 0}      # Open
    NAUTICAL_MILE_TO_KM = 1.852
    distance_table_km = { pair: round(nm * NAUTICAL_MILE_TO_KM, 2) for pair, nm in distance_table_nm.items()}

    vehicle_speeds = 44 # km/h (max speed)
    vehicle_speeds_effective = vehicle_speeds* (24/divisions_per_day) # convert to current timeperiods
    # Assumptions
    m = 0.1                   # Mean travel experiances a 10% delay
    CV = 0.2                   # 20% variability

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



