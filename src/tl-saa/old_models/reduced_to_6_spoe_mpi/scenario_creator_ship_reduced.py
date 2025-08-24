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
