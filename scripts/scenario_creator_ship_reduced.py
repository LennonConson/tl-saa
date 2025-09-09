import numpy as np
from scipy.stats import lognorm
import csv
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
def generate_ship_travel_times(divisions_per_day , percentile_delays, average_delay=0.15, sigma=1.0, num_V=8):
    # Pre-Departure Delays
    # Exponential Distribution
    
    # In-Transit Delays
    
    distance_table_nm = {
            ( 6,  6): 0,      ( 6,  7): 408,    ( 6,  8): 1336, ( 6,  9): 1226, ( 6, 10): 1475, ( 6, 11): 1662, ( 6, 12): 5210.5, # Beaumont
            ( 7,  6): 408,    ( 7,  7): 0,      ( 7,  8): 1120, ( 7,  9): 1014, ( 7, 10): 1261, ( 7, 11): 1449, ( 7, 12): 4904,   # Gulfport
            ( 8,  6): 1336,   ( 8,  7): 1120,   ( 8,  8): 0,    ( 8,  9): 199,  ( 8, 10): 219,  ( 8, 11): 429,  ( 8, 12): 4904,   # Charleston
            ( 9,  6): 1226,   ( 9,  7): 1014,   ( 9,  8): 199,  ( 9,  9): 0,    ( 9, 10): 376,  ( 9, 11): 592,  ( 9, 12): 4904,   # Jacksonville
            (10,  6): 1475,   (10,  7): 1261,   (10,  8): 219,  (10,  9): 376,  (10, 10): 0,    (10, 11): 254,  (10, 12): 3678,   # Morehead City
            (11,  6): 1662,   (11,  7): 1449,   (11,  8): 429,  (11,  9): 592,  (11, 10): 254,  (11, 11): 0,    (11, 12): 3678,   # Portsmouth
            ( 0,  6): 0,      ( 0,  7): 0,      ( 0,  8): 0,    ( 0,  9): 0,    ( 0, 10): 0,    ( 0, 11): 0,    ( 0, 12): 0}      # Open
    
    NAUTICAL_MILE_TO_KM = 1.852
    distance_table_km = { pair: round(nm * NAUTICAL_MILE_TO_KM, 2) for pair, nm in distance_table_nm.items()}

    vehicle_speeds = 44 # km/h (max speed)

    # Calculate time to reach destination in hours for each (origin, destination) pair
    time_to_reach_destination = {}
    for (A, B), distance_km in distance_table_km.items():
        time_to_reach_destination[(A, B)] = distance_km / vehicle_speeds
    
    perturbed_time_to_reach_destination = {}
    for (A, B), time_hr in time_to_reach_destination.items():
        if time_hr == 0:
            perturbed_time_to_reach_destination[(A, B)] = 0
            continue
        scale = average_delay * time_hr
        if B == 0 or B == 12:
            percentile_delay = percentile_delays[A]
        else:
            percentile_delay = percentile_delays[A] * percentile_delays[B]
        log_normal_adjustment = lognorm.ppf(percentile_delay, s=sigma, loc=0, scale=scale)
        perturbed_time_to_reach_destination[(A, B)] = time_hr + log_normal_adjustment
    
    
    CONVERT_TIME = divisions_per_day/24 # convert to current timeperiods
    
    ship_travel_times = {k: v * CONVERT_TIME for k, v in perturbed_time_to_reach_destination.items()}


    ship_travel_times_with_ship = {}

    for (A, B), travel_time in ship_travel_times.items():
        for v in range(1,num_V+1):
            ship_travel_times_with_ship[(A, B, v)] = round(travel_time)
            

    return ship_travel_times_with_ship
