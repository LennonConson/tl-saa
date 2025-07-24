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
            ( 7,  7): 0,      ( 7,  8): 408,    ( 7,  9): 1336, ( 7, 10): 1226, ( 7, 11): 1475, ( 7, 12): 1662, ( 7, 13): 5210.5, # Beaumont
            ( 8,  7): 408,    ( 8,  8): 0,      ( 8,  9): 1120, ( 8, 10): 1014, ( 8, 11): 1261, ( 8, 12): 1449, ( 8, 13): 4904,   # Gulfport
            ( 9,  7): 1336,   ( 9,  8): 1120,   ( 9,  9): 0,    ( 9, 10): 199,  ( 9, 11): 219,  ( 9, 12): 429,  ( 9, 13): 4904,   # Charleston
            (10,  7): 1226,   (10,  8): 1014,   (10,  9): 199,  (10, 10): 0,    (10, 11): 376,  (10, 12): 592,  (10, 13): 4904,   # Jacksonville
            (11,  7): 1475,   (11,  8): 1261,   (11,  9): 219,  (11, 10): 376,  (11, 11): 0,    (11, 12): 254,  (11, 13): 3678,   # Morehead City
            (12,  7): 1662,   (12,  8): 1449,   (12,  9): 429,  (12, 10): 592,  (12, 11): 254,  (12, 12): 0,    (12, 13): 3678,   # Portsmouth
            ( 0,  7): 0,      ( 0,  8): 0,      ( 0,  9): 0,    ( 0, 10): 0,    ( 0, 11): 0,    ( 0, 12): 0,    ( 0, 13): 0}      # Open
    
    NAUTICAL_MILE_TO_KM = 1.852
    distance_table_km = { pair: round(nm * NAUTICAL_MILE_TO_KM, 2) for pair, nm in distance_table_nm.items()}

    vehicle_speeds = 44 # km/h (max speed)

    # Calculate time to reach destination in hours for each (origin, destination) pair
    time_to_reach_destination = {}
    for (A, B), distance_km in distance_table_km.items():
        time_to_reach_destination[(A, B)] = distance_km / vehicle_speeds
    
    # Assumptions
    average_delay = 0.15                   # Mean travel experiences a 25  % delay
    sigma = 1.0                     # Standard deviation for log-normal distribution

    perturbed_time_to_reach_destination = {}
    for (A, B), time_hr in time_to_reach_destination.items():
        if time_hr == 0:
            perturbed_time_to_reach_destination[(A, B)] = 0
            continue
        scale = average_delay * time_hr
        log_normal_adjustment = lognorm.ppf(percentile_delays[A], s=sigma, loc=0, scale=scale)
        perturbed_time_to_reach_destination[(A, B)] = time_hr + log_normal_adjustment
    
    
    CONVERT_TIME = divisions_per_day/24 # convert to current timeperiods
    
    ship_travel_times = {k: v * CONVERT_TIME for k, v in perturbed_time_to_reach_destination.items()}


    ship_travel_times_with_ship = {}

    for (A, B), travel_time in ship_travel_times.items():
        for v in range(1,num_V+1):
            ship_travel_times_with_ship[(A, B, v)] = round(travel_time)
            

    return ship_travel_times_with_ship


print(generate_ship_travel_times(3 , {7:.98,8:.98,9:.98,10:.98,11:.98,12:.98}, average_delay=0.15, sigma=1.0, num_V=1))