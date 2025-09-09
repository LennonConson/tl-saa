from scipy.stats import lognorm

def generate_rail_travel_times(divisions_per_day, percentile_delays, average_delay=0.15, sigma=1.0):
    travel_time_by_rail = { ( 1, 1): 7,  ( 1, 2): 8,  ( 1, 3): 4,  ( 1, 4): 2,  ( 1, 5): 4,  ( 1, 6): 6,    # Fort Stewart
                            ( 2, 1): 11, ( 2, 2): 8,  ( 2, 3): 1,  ( 2, 4): 2,  ( 2, 5): 4,  ( 2, 6): 1,    # Fort Bragg
                            ( 3, 1): 10, ( 3, 2): 8,  ( 3, 3): 1,  ( 3, 4): 7,  ( 3, 5): 4,  ( 3, 6): 4,    # Camp Lejeune
                            ( 4, 1): 2,  ( 4, 2): 3,  ( 4, 3): 10, ( 4, 4): 8,  ( 4, 5): 11, ( 4, 6): 10,   # Fort Polk
                            ( 5, 1): 4,  ( 5, 2): 3,  ( 5, 3): 7,  ( 5, 4): 7,  ( 5, 5): 8,  ( 5, 6): 8,  } # Camp Shelby

    # Assuming the above travel times have been rounded to the nearest hour
    # we try to reintroduce non-integer travel times by adding a small random value
    # travel_time_by_rail_hours = {
    #     key: 24*(value + random.uniform(-0.5, 0.4999999999999999))
    #     for key, value in travel_time_by_rail.items()
    # }
    # print(travel_time_by_rail_hours)
    travel_time_by_rail_hours = {(1, 1): 179.4688943939543, (1, 2): 187.42417735164793, (1, 3): 96.59190670335616, (1, 4): 37.20867269825564, (1, 5): 96.25389033669065, (1, 6): 136.30964719956572, (2, 1): 265.41678852834497, (2, 2): 185.4585365817324, (2, 3): 27.55413497689113, (2, 4): 41.91110992218494, (2, 5): 88.33982845063801, (2, 6): 15.782241504008425, (3, 1): 231.08109685412944, (3, 2): 196.11284507589454, (3, 3): 16.03414994600847, (3, 4): 159.9993519218197, (3, 5): 101.35816354120503, (3, 6): 99.1760225462851, (4, 1): 45.16079472510921, (4, 2): 66.35984192985268, (4, 3): 245.19079171442354, (4, 4): 184.12272606815876, (4, 5): 260.8272732962638, (4, 6): 232.03508593869313, (5, 1): 96.36727160370307, (5, 2): 63.77768640015512, (5, 3): 173.16604483566877, (5, 4): 164.5418089894359, (5, 5): 199.85254053787645, (5, 6): 181.06506946084866}

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

