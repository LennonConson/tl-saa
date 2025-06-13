# Going down to single SPOD
import time
import pickle
import pandas as pd

start_time = time.time()

import pyomo.environ as pyo
import random
max_days = 30
divisions_per_day = 2
u_open = 3
num_I = 20
num_J = 10
num_K = 1
num_V = 40
num_T = divisions_per_day * max_days

outload_requirements = {1: 182645, 2: 177767, 3: 149069, 4: 162234, 5: 231899, 6: 165908, 7: 192020, 8: 192637, 9: 201447, 10: 157508, 11: 162219, 12: 153887, 13: 165353, 14: 172762, 15: 151992, 16: 228399, 17: 219917, 18: 156764, 19: 232328, 20: 194919}



daily_processing_rate = {1: 119000, 2: 105000, 3: 109300, 4: 110000, 5: 88000, 6: 89300, 7: 108300, 8: 57300, 9: 84000, 10: 123100}
updated_daily_processing_rate = {k + num_I: v for k, v in daily_processing_rate.items()}

ship_layberth = {1:7, 2:7, 3:2, 4:6, 5:2, 6:3, 7:3, 8:3, 9:3, 10:3, 11:3, 12:7, 13:7, 14:7, 15:8, 16:10, 17:9, 18:10, 19:2, 20:2, 21:7, 22:6, 23:6, 24:6, 25:1, 26:1, 27:1, 28:1, 29:1, 30:6, 31:6, 32:7, 33:6, 34:1, 35:1, 36:1, 37:1, 38:1, 39:5, 40:10}
updated_ship_layberth = {k: v + num_I for k, v in ship_layberth.items()}

ship_berth_binary = {}
for ship, assigned_berth in updated_ship_layberth.items():
    for berth in range(num_I+1, num_I + num_J +1):
        if berth == assigned_berth:
            ship_berth_binary[(berth, ship)] = 1
        else:
            ship_berth_binary[(berth, ship)] = 0

stowable_cargo_capacity = {1: 99290, 2: 142099, 3: 139553, 4: 139553, 5: 142099, 6: 117137, 7: 117137, 8: 117137, 9: 117137, 10: 117137, 11: 112960, 12: 126335, 13: 126335, 14: 126335, 15: 104066, 16: 104066, 17: 104066, 18: 104066, 19: 102827, 20: 102827, 21: 83146, 22: 123419, 23: 123419, 24: 123419, 25: 80933, 26: 82521, 27: 82521, 28: 91886, 29: 91886, 30: 207171, 31: 207171, 32: 144874, 33: 144874, 34: 139553, 35: 142099, 36: 105137, 37: 105137, 38: 105137, 39: 271363, 40: 271363}

# # travel_time_by_rail = {(1, 1): 1, (1, 2): 8, (1, 3): 12, (1, 4): 11, (1, 5): 12, (1, 6): 15, (1, 7): 14, (1, 8): 12, (1, 9): 10, (1, 10): 18, (2, 1): 19, (2, 2): 23, (2, 3): 27, (2, 4): 21, (2, 5): 25, (2, 6): 22, (2, 7): 7, (2, 8): 9, (2, 9): 12, (2, 10): 1, (3, 1): 5, (3, 2): 5, (3, 3): 7, (3, 4): 6, (3, 5): 8, (3, 6): 6, (3, 7): 19, (3, 8): 19, (3, 9): 19, (3, 10): 17, (4, 1): 8, (4, 2): 11, (4, 3): 13, (4, 4): 13, (4, 5): 19, (4, 6): 17, (4, 7): 10, (4, 8): 7, (4, 9): 8, (4, 10): 13, (5, 1): 15, (5, 2): 14, (5, 3): 21, (5, 4): 20, (5, 5): 21, (5, 6): 24, (5, 7): 8, (5, 8): 4, (5, 9): 1, (5, 10): 9, (6, 1): 7, (6, 2): 8, (6, 3): 4, (6, 4): 2, (6, 5): 4, (6, 6): 6, (6, 7): 23, (6, 8): 21, (6, 9): 22, (6, 10): 23, (7, 1): 11, (7, 2): 8, (7, 3): 1, (7, 4): 2, (7, 5): 4, (7, 6): 1, (7, 7): 22, (7, 8): 24, (7, 9): 21, (7, 10): 27, (8, 1): 9, (8, 2): 9, (8, 3): 11, (8, 4): 11, (8, 5): 9, (8, 6): 9, (8, 7): 17, (8, 8): 20, (8, 9): 18, (8, 10): 13, (9, 1): 6, (9, 2): 10, (9, 3): 15, (9, 4): 13, (9, 5): 20, (9, 6): 16, (9, 7): 9, (9, 8): 11, (9, 9): 10, (9, 10): 9, (10, 1): 10, (10, 2): 8, (10, 3): 1, (10, 4): 7, (10, 5): 4, (10, 6): 4, (10, 7): 25, (10, 8): 24, (10, 9): 21, (10, 10): 25, (11, 1): 7, (11, 2): 6, (11, 3): 8, (11, 4): 8, (11, 5): 8, (11, 6): 5, (11, 7): 20, (11, 8): 20, (11, 9): 19, (11, 10): 17, (12, 1): 8, (12, 2): 5, (12, 3): 9, (12, 4): 11, (12, 5): 10, (12, 6): 10, (12, 7): 15, (12, 8): 15, (12, 9): 14, (12, 10): 15, (13, 1): 14, (13, 2): 11, (13, 3): 5, (13, 4): 9, (13, 5): 7, (13, 6): 6, (13, 7): 24, (13, 8): 21, (13, 9): 21, (13, 10): 21, (14, 1): 12, (14, 2): 11, (14, 3): 8, (14, 4): 6, (14, 5): 6, (14, 6): 1, (14, 7): 21, (14, 8): 23, (14, 9): 22, (14, 10): 21, (15, 1): 2, (15, 2): 3, (15, 3): 10, (15, 4): 8, (15, 5): 11, (15, 6): 10, (15, 7): 17, (15, 8): 13, (15, 9): 13, (15, 10): 20, (16, 1): 5, (16, 2): 8, (16, 3): 10, (16, 4): 12, (16, 5): 16, (16, 6): 15, (16, 7): 13, (16, 8): 16, (16, 9): 13, (16, 10): 20, (17, 1): 13, (17, 2): 15, (17, 3): 23, (17, 4): 18, (17, 5): 22, (17, 6): 23, (17, 7): 4, (17, 8): 4, (17, 9): 3, (17, 10): 11, (18, 1): 8, (18, 2): 7, (18, 3): 5, (18, 4): 7, (18, 5): 5, (18, 6): 6, (18, 7): 20, (18, 8): 17, (18, 9): 17, (18, 10): 18, (19, 1): 6, (19, 2): 5, (19, 3): 11, (19, 4): 12, (19, 5): 12, (19, 6): 11, (19, 7): 17, (19, 8): 16, (19, 9): 13, (19, 10): 17, (20, 1): 4, (20, 2): 3, (20, 3): 7, (20, 4): 7, (20, 5): 8, (20, 6): 8, (20, 7): 18, (20, 8): 18, (20, 9): 18, (20, 10): 21}
# # travel_time_by_rail = {
# #     key: value + random.uniform(-0.500001, 0.5)
# #     for key, value in travel_time_by_rail.items()
# # }

travel_time_by_rail = {(1, 1): 0.8314959200678788, (1, 2): 7.651274760314795, (1, 3): 11.94121352163306, (1, 4): 11.076943367016806, (1, 5): 12.061965517532897, (1, 6): 14.954727982797039, (1, 7): 14.13591877438131, (1, 8): 12.067038253620506, (1, 9): 10.202556891243376, (1, 10): 17.749086879874103,
                       (2, 1): 18.604677841746952, (2, 2): 23.18273460291128, (2, 3): 27.165439727263262, (2, 4): 21.3228373618454, (2, 5): 24.695380753898597, (2, 6): 21.65284183644084, (2, 7): 6.814188820963884, (2, 8): 8.74567823872299, (2, 9): 12.263362817599614, (2, 10): 1.3581579018035135, (3, 1): 4.561239760686096, (3, 2): 4.88514035066151, (3, 3): 7.4730022851160465, (3, 4): 5.818479686426855, (3, 5): 7.959535728456184, (3, 6): 6.415355061800198, (3, 7): 18.77278463389479, (3, 8): 19.133158064157318, (3, 9): 18.944043476776, (3, 10): 17.49854151365423, (4, 1): 8.101051087524725, (4, 2): 10.951365599782678, (4, 3): 13.450566226440673, (4, 4): 12.861968385811911, (4, 5): 18.70564310231278, (4, 6): 17.051152626271136, (4, 7): 10.46953876441811, (4, 8): 6.529731820532948, (4, 9): 8.480952971910938, (4, 10): 13.46503048502768, (5, 1): 14.728246853503114, (5, 2): 13.799542910244947, (5, 3): 21.123612895831695, (5, 4): 20.088936870876033, (5, 5): 21.349463748261652, (5, 6): 24.307048475234005, (5, 7): 7.961540005122725, (5, 8): 3.5494698094080093, (5, 9): 1.3556142330737766, (5, 10): 9.276618468675466, (6, 1): 6.831267471593927, (6, 2): 8.097933971060433, (6, 3): 4.08809047667249, (6, 4): 1.7505423970922658, (6, 5): 4.244009957389786, (6, 6): 5.553203004916493, (6, 7): 22.50076494708662, (6, 8): 20.700925234998685, (6, 9): 22.374408192914398, (6, 10): 23.127321599629525, (7, 1): 11.042043986808057, (7, 2): 7.655347058490766, (7, 3): 0.5060326283546839, (7, 4): 2.0757711674103634, (7, 5): 4.415513023387343, (7, 6): 1.0878046726675916, (7, 7): 22.418195027043925, (7, 8): 23.829433629842256, (7, 9): 20.58094204694538, (7, 10): 26.735695896612093, (8, 1): 9.09617905077384, (8, 2): 8.545062563650754, (8, 3): 11.162624892073854, (8, 4): 10.957597967408503, (8, 5): 8.901918778520963, (8, 6): 8.999634637812097, (8, 7): 17.334564284389188, (8, 8): 19.544871525177506, (8, 9): 18.462107477038423, (8, 10): 12.626862167096355, (9, 1): 5.715448683863134, (9, 2): 9.98204757070291, (9, 3): 14.6888866612359, (9, 4): 13.416774645082558, (9, 5): 20.45106247894115, (9, 6): 16.38693789734484, (9, 7): 9.20026199851782, (9, 8): 10.55537875525591, (9, 9): 10.226877896406664, (9, 10): 8.939243007930653, (10, 1): 9.664411171340967, (10, 2): 8.28301780216345, (10, 3): 1.446653319468309, (10, 4): 6.546410839422283, (10, 5): 3.8455428501009283, (10, 6): 4.198635805743216, (10, 7): 24.8609341874661, (10, 8): 23.52723967439802, (10, 9): 21.31946207351918, (10, 10): 24.88905870388831, (11, 1): 7.383569693934771, (11, 2): 5.615228717586522, (11, 3): 7.8482251538521135, (11, 4): 8.34473089522072, (11, 5): 8.49668890610535, (11, 6): 4.736218617134506, (11, 7): 20.253048788674356, (11, 8): 20.42395849549627, (11, 9): 19.349259971983866, (11, 10): 17.291599265792417, (12, 1): 7.57922587402787, (12, 2): 5.205448113453997, (12, 3): 8.9791979919804, (12, 4): 10.875779737082679, (12, 5): 9.684624706581326, (12, 6): 9.967525293141767, (12, 7): 15.456277968688724, (12, 8): 15.482813315694642, (12, 9): 14.046590477193034, (12, 10): 15.114107039741793, (13, 1): 14.142370499667274, (13, 2): 11.363210554870818, (13, 3): 4.663374952860642, (13, 4): 9.393806932828532, (13, 5): 6.673288099954429, (13, 6): 5.86545336103693, (13, 7): 24.072482756820694, (13, 8): 21.40815899331547, (13, 9): 21.111002442662016, (13, 10): 21.2065989917024, (14, 1): 12.283394521844748, (14, 2): 11.267228995300508, (14, 3): 8.452754307829712, (14, 4): 6.455894509998084, (14, 5): 6.275338027768645, (14, 6): 1.3068009064674415, (14, 7): 20.978974209372208, (14, 8): 23.176396918585237, (14, 9): 21.536293377691983, (14, 10): 21.09640931492207, (15, 1): 2.4076393997586862, (15, 2): 2.6770512002346134, (15, 3): 9.942616502137906, (15, 4): 7.5082836014327015, (15, 5): 10.634761911655685, (15, 6): 9.61101790396358, (15, 7): 16.855343942593844, (15, 8): 12.829781925414878, (15, 9): 13.222490307847918, (15, 10): 19.898572374232838, (16, 1): 5.37301688531437, (16, 2): 8.057830130162998, (16, 3): 10.352437729050493, (16, 4): 11.684477643682543, (16, 5): 16.297893103724203, (16, 6): 14.663090362080176, (16, 7): 12.919579022802843, (16, 8): 15.767491254434297, (16, 9): 13.141099320681944, (16, 10): 19.835993482709153, (17, 1): 12.89724446785151, (17, 2): 15.112505331330533, (17, 3): 23.136670890284233, (17, 4): 17.79037130314954, (17, 5): 21.86926752090584, (17, 6): 22.525367847305183, (17, 7): 4.462588301398737, (17, 8): 3.5171869301487684, (17, 9): 2.524029261055131, (17, 10): 10.784295760374825, (18, 1): 7.574880907456144, (18, 2): 7.372627327378215, (18, 3): 4.865245881365021, (18, 4): 7.314312528095623, (18, 5): 5.282376059781825, (18, 6): 6.081926684824206, (18, 7): 20.36628276107256, (18, 8): 17.460050377786033, (18, 9): 17.457210726291947, (18, 10): 17.94583601852058, (19, 1): 6.232258184037768, (19, 2): 4.639169471121598, (19, 3): 11.48477634216164, (19, 4): 11.926395380937866, (19, 5): 12.00054399450338, (19, 6): 10.688938935539445, (19, 7): 16.675564273687286, (19, 8): 16.313296109031185, (19, 9): 12.990911892303103, (19, 10): 16.503326251703324, (20, 1): 4.470287375071521, (20, 2): 3.2096890802902602, (20, 3): 7.442472121956893, (20, 4): 7.4806923583053795, (20, 5): 7.818087648488676, (20, 6): 8.40130273269599, (20, 7): 17.589828304329345, (20, 8): 17.714338748877278, (20, 9): 18.17473293905467, (20, 10): 21.434831172849886}

updated_travel_time_by_rail = { (k[0], k[1] + num_I ,0): v for k, v in travel_time_by_rail.items() }


for key, travel_time in updated_travel_time_by_rail.items():
    updated_travel_time_by_rail[key] = round(travel_time * divisions_per_day)
# TODO Fix SPOE numbers to be dynamically updated
distance_table = {
    (21, 21): 0,      (21, 22): 408,    (21, 23): 1336, (21, 24): 1226, (21, 25): 1475, (21, 26): 1662, (21, 27): 4791,   (21, 28): 4457,   (21, 29): 4389, (21, 30): 5570,   (21, 31): 5210.5,
    (22, 21): 408,    (22, 22): 0,      (22, 23): 1120, (22, 24): 1014, (22, 25): 1261, (22, 26): 1449, (22, 27): 4644,   (22, 28): 4310,   (22, 29): 4242, (22, 30): 5423,   (22, 31): 4904,
    (23, 21): 1336,   (23, 22): 1120,   (23, 23): 0,    (23, 24): 199,  (23, 25): 219,  (23, 26): 429,  (23, 27): 4845,   (23, 28): 4511,   (23, 29): 4443, (23, 30): 5624,   (23, 31): 4904,
    (24, 21): 1226,   (24, 22): 1014,   (24, 23): 199,  (24, 24): 0,    (24, 25): 376,  (24, 26): 592,  (24, 27): 4790,   (24, 28): 4456,   (24, 29): 4388, (24, 30): 5569,   (24, 31): 4904,
    (25, 21): 1475,   (25, 22): 1261,   (25, 23): 219,  (25, 24): 376,  (25, 25): 0,    (25, 26): 254,  (25, 27): 4909,   (25, 28): 4575,   (25, 29): 4507, (25, 30): 5688,   (25, 31): 3678,
    (26, 21): 1662,   (26, 22): 1449,   (26, 23): 429,  (26, 24): 592,  (26, 25): 254,  (26, 26): 0,    (26, 27): 5066,   (26, 28): 4732,   (26, 29): 4664, (26, 30): 5845,   (26, 31): 3678,
    (27, 21): 4791,   (27, 22): 4644,   (27, 23): 4845, (27, 24): 4790, (27, 25): 4909, (27, 26): 5066, (27, 27): 0,      (27, 28): 369,    (27, 29): 453,  (27, 30): 816,    (27, 31): 8275.5,
    (28, 21): 4457,   (28, 22): 4310,   (28, 23): 4511, (28, 24): 4456, (28, 25): 4575, (28, 26): 4732, (28, 27): 369,    (28, 28): 0,      (28, 29): 95,   (28, 30): 1165,   (28, 31): 7969,
    (29, 21): 4389,   (29, 22): 4242,   (29, 23): 4443, (29, 24): 4388, (29, 25): 4507, (29, 26): 4664, (29, 27): 453,    (29, 28): 95,     (29, 29): 0,    (29, 30): 1229,   (29, 31): 7969,
    (30, 21): 5570,   (30, 22): 5423,   (30, 23): 5624, (30, 24): 5569, (30, 25): 5688, (30, 26): 5845, (30, 27): 816,    (30, 28): 1165,   (30, 29): 1229, (30, 30): 0,      (30, 31): 9195,
    (0, 21): 0,       (0, 22): 0,       (0, 23): 0,     (0, 24): 0,     (0, 25): 0,     (0, 26): 0,     (0, 27): 0,       (0, 28): 0,       (0, 29): 0,     (0, 30): 0,       (0, 31): 0
}

vehicle_speeds = {
    1: 417, 2: 633, 3: 630, 4: 630, 5: 630, 6: 310, 7: 310, 8: 310, 9: 310, 10: 310,
    11: 310, 12: 350, 13: 350, 14: 350, 15: 380, 16: 370, 17: 380, 18: 370, 19: 324, 20: 324,
    21: 350, 22: 375, 23: 375, 24: 375, 25: 303, 26: 303, 27: 303, 28: 303, 29: 303, 30: 322,
    31: 322, 32: 633, 33: 630, 34: 619, 35: 619, 36: 475, 37: 475, 38: 475, 39: 487, 40: 470
}

ship_travel_times = {}
for (A, B), distance in distance_table.items():
    for vehicle, speed in vehicle_speeds.items():
        ship_travel_times[(A, B, vehicle)] = distance / speed if speed != 0 else float('inf')

for key, travel_time in ship_travel_times.items():
    ship_travel_times[key] = round(travel_time * divisions_per_day)

travel_times = {
    **updated_travel_time_by_rail, 
    **ship_travel_times
}

model = pyo.ConcreteModel()
# Sets
# --------------
# I the set of origins
model.I = pyo. Set(initialize = range(1, num_I+1))
# J the set of transshipment nodes/SPOEs
model.J = pyo.Set(initialize = range(num_I + 1 , num_I +num_J+1))
model.J_0 = pyo.Set(initialize = [0]+ list(range(num_I + 1 , num_I +num_J+1)))
# # K the set of destinations/SPODs
model.K = pyo.Set(initialize = range(num_I +num_J+1, num_I + num_J + num_K+1))
# # # JK the set of destinations/SPODs
model.M = pyo.Set(initialize = range(num_I +1, num_I + num_J + num_K+1))
# # # IJK the set of destinations/SPODs
model.N = pyo.Set(initialize = range(1, num_I + num_J + num_K+1))

model.N_0 = pyo.Set(initialize = range(num_I + num_J + num_K+1))

# model.N_0 = pyo.Set(initialize = range( num_I + num_J + num_K+1))
# # V the set of ships
model.V = pyo.Set(initialize = range(1,num_V+1))
# # V the set of ships
model.V_0 = pyo.Set(initialize = range(num_V+1))
# # T the set of ships
model.T = pyo.Set(initialize = range(1, num_T+1))
model.T_0 = pyo.Set(initialize = range(num_T+1))
model.D = pyo.Set(initialize = range(1,max_days+1))

# # Parameters
# # ---------
# # Outload Requirements
model.a_i  = pyo.Param(model.I,           initialize=outload_requirements, within=pyo.NonNegativeReals)
# # Outload Requirements
model.b_jv  = pyo.Param(model.J, model.V,           initialize=ship_berth_binary,  within=pyo.NonNegativeReals)
# Travel Times
model.c_nnv  = pyo.Param(model.N_0, model.N, model.V_0,           initialize=travel_times, within=pyo.NonNegativeReals)
# tau days number of time windows per day
# model.tau   = pyo.Param(                    initialize=divisions_per_day, within=pyo.NonNegativeReals)
# maximum number of spoes
model.u_open   = pyo.Param(                    initialize=u_open, within=pyo.NonNegativeReals)
# Stowable Cargo Capacity
model.u_ship   = pyo.Param(model.V,                    initialize=stowable_cargo_capacity, within=pyo.NonNegativeReals)
# Daily Processing Rate
model.u_spoe   = pyo.Param(model.J,                    initialize=updated_daily_processing_rate, within=pyo.NonNegativeReals)

max_travel = max(
    model.c_nnv[index] 
    for index in model.c_nnv
)


model.T_prime = pyo.Set(initialize = range(num_T+max_travel+1))

# Define Decision Variables
# ------------------------
# Utilization of port J
model.y_open     = pyo.Var(model.J, domain=pyo.Binary, initialize=0)
# The amount of equipment that arrives at time T from/at/to IJK
model.x_rail  = pyo.Var(model.I, model.J, model.T, domain=pyo.NonNegativeReals, initialize=0)
model.y_rail  = pyo.Var(model.I, model.J, model.T, domain=pyo.Binary, initialize=0)
# model.x_ship_in  = pyo.Var(model.J_0, model.M, model.K, model.V, model.T_0, domain=pyo.NonNegativeReals, initialize=0)
# The amount of equipment that arrives at time T from/at/to IJK
model.x_ship_out = pyo.Var(model.J_0, model.M, model.V, model.T_0, domain=pyo.NonNegativeReals, initialize=0)
# The amount of equipment that arrives at time T from/at/to IJK
# model.y_ship_in  = pyo.Var(model.J_0, model.M, model.K, model.V, model.T_0, domain=pyo.Binary, initialize=0)
model.y_ship_out = pyo.Var(model.J_0, model.M, model.V, model.T_0, domain=pyo.Binary, initialize=0)
# model.active_ship_k = pyo.Var(model.K, model.V, domain=pyo.Binary, initialize=0)

# Objective Funtion
def objective_rule(model):
    return sum((model.c_nnv[j,k,v] + t) * model.x_ship_out[j,k,v,t] for j in model.J for k in model.K for v in model.V for t in model.T)
model.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

# TIER 1 TASK: Connect x-rail to y-rail
# STATUS: V&V
# 21
def const_x_rail_to_y(model, i, j, t):
    return model.x_rail[i,j,t]  <= model.u_spoe[j] * model.y_rail[i,j,t]
model.const_x_rail_to_y = pyo.Constraint(model.I, model.J, model.T, rule=const_x_rail_to_y)

# TIER 1 TASK: Ship connect x to y
# STATUS: V&V
# TODO: Fix M
# 22
def const_x_ship_out_to_y(model, j, m, v,t):
    return model.x_ship_out[j,m,v,t]  <= model.u_ship[v] * model.y_ship_out[j,m,v,t]
model.const_x_ship_out_to_y = pyo.Constraint(model.J, model.M, model.V, model.T, rule=const_x_ship_out_to_y)

##############
# ENTITY: SPOE
##############
# # TIER 1 TASK: Check max spoes are opened
# # STATUS: V&V
# # 23
# def const_u_spoe(model):
#     return sum(model.y_open[j] for j in model.J) <= model.u_open
# model.const_u_spoe = pyo.Constraint(rule=const_u_spoe)

# # # TIER 1 TASK: Make sure only use open ports
# # # STATUS: V&V
# # # 24
# def const_only_open_rail(model, i, j, t):
#     return  model.y_rail[i,j,t] <= model.y_open[j]
# model.const_only_open_rail = pyo.Constraint(model.I, model.J, model.T, rule=const_only_open_rail)

# # # 25
# def const_only_open_ship_out(model, j, m, v, t):
#     return  model.y_ship_out[j,m,v,t] <= model.y_open[j]
# model.const_only_open_ship_out = pyo.Constraint(model.J, model.M, model.V, model.T, rule=const_only_open_ship_out)

# # 26
# def const_only_open_ship_in(model, j, j_prime, v, t):
#     return  model.y_ship_out[j,j_prime,v,t] <= model.y_open[j_prime]
# model.const_only_open_ship_in = pyo.Constraint(model.J, model.J, model.V, model.T, rule=const_only_open_ship_in)


##############
# ENTITY: Rail
##############


# TIER 1 TASK: Make sure all rolling stock departs I.
# STATUS: V&V
# 27
def cont_outload(model, i):
    return sum(model.x_rail[i,j,t] for j in model.J for t in model.T) == model.a_i[i]
model.cont_outload = pyo.Constraint(model.I, rule=cont_outload)

# TIER 1 TASK: Make sure daily processing is observed
# STATUS: V&V
# 28
def const_daily_processing(model, j, d):
        return sum(model.x_rail[i,j,t]
                for i in model.I
                for t in range(divisions_per_day  * (d - 1) +1, divisions_per_day  * d))  <= model.u_spoe[j]
model.const_daily_processing = pyo.Constraint(model.J, model.D, rule=const_daily_processing)

# TIER 1 TASK: Make sure that a ship does not depart before the beginin of time horizon.
# STATUS: V&V
# 29
def const_start_time(model, i, j, t):
    if t > model.c_nnv[i,j,0]:
        return pyo.Constraint.Skip
    return model.y_rail[i, j, t] == 0
model.const_start_time= pyo.Constraint(model.I, model.J, model.T, rule=const_start_time)

##############
# ENTITY: Ship
##############

# TIER 1 TASK: Ship Pathing
# STATUS: V&V

# TIER 2 TASK: Set layberth port
# STATUS: V&V
# 30
def const_layberth(model, j, v):
    return model.y_ship_out[0, j, v, 0] == model.b_jv[j,v]
model.const_layberth = pyo.Constraint(model.J, model.V, rule=const_layberth)

# TIER 2 TASK: Ensure SPOE 0 is not used outside of time 0.
# STATUS: V&V
# 31
def const_illegal_layberth_out(model):
    return sum(
        model.y_ship_out[0, m, v, t]
        for m in model.M
        for v in model.V
        for t in model.T
    ) == 0
model.const_illegal_layberth_out = pyo.Constraint(rule=const_illegal_layberth_out)

# TIER 2 TASK: Ensure at time 0 only layberths origins are used.
# STATUS: V&V
# 32
def const_illegal_time_0(model):
    return sum(
        model.y_ship_out[j, m, v, 0]
        for j in model.J
        for m in model.M
        for v in model.V
    ) == 0
model.const_illegal_time_0 = pyo.Constraint(rule=const_illegal_time_0)

# TIER 2 TASK: Ensure that all ships that go through a J go somewhere.
# STATUS: V&V
# 33
def const_intermediate_nodes(model, j, v):
    return (
        sum(model.y_ship_out[j_prime, j, v, t] for j_prime in model.J_0 if j_prime != j for t in model.T_0)
        == sum(model.y_ship_out[j, m, v, t] for m in model.M if m != j for t in model.T)
    )
model.const_intermediate_nodes = pyo.Constraint(model.J, model.V, rule=const_intermediate_nodes)


# TIER 2 TASK: Ensure that all ships go to SPOD once.
# STATUS: V&V
# 34
def const_destination_nodes(model, v):
    return (sum(model.y_ship_out[j, k, v, t] for j in model.J for k in model.K for t in model.T)
            == 1)
model.const_destination_nodes = pyo.Constraint(model.V, rule=const_destination_nodes)

# # TIER 2 TASK: Make sure ships only visit spoe once.
# # STATUS: V&V
# # 34
# def const_one_visit_ship_out(model, j, v):
#     return sum(
#         model.y_ship_out[j_prime, j, k, v, t]
#         for j_prime in model.J_0 if j != j_prime
#         for k in model.K
#         for t in model.T
#     ) <= 1
# model.const_one_visit_ship_out = pyo.Constraint(model.J, model.V, rule=const_one_visit_ship_out)


# # TIER 2 TASK: Make sure ships only visit depart spoe once.
# # STATUS: V&V
# # 34
# def const_one_depart_ship_out(model, j, v):
#     return sum(
#         model.y_ship_out[j, m, k, v, t]
#         for m in model.M if j != m
#         for k in model.K
#         for t in model.T
#     ) <= 1
# model.const_one_depart_ship_out = pyo.Constraint(model.J_0, model.V, rule=const_one_depart_ship_out)


# # TIER 2 TASK: Make sure ships don't go to same port.
# # STATUS: V&V
# # NOTE: Probably unneeded
# # 35
# def const_ship_loop(model, j):
#     return (sum(
#         model.y_ship_out[j, j, k, v, t]
#         for k in model.K
#         for v in model.V
#         for t in model.T
#     ) == 0)
# model.const_ship_loop = pyo.Constraint(model.J, rule=const_ship_loop)



# TIER 1 TASK: Ship Capacity
# STATUS: V&V
# 35
def const_ship_capacity(model, v, t):
    return sum(model.x_ship_out[j,m,v,t] for j  in model.J for m in model.M if j != m ) <= model.u_ship[v]
model.const_ship_capacity = pyo.Constraint(model.V, model.T, rule=const_ship_capacity)


##############
# ENTITY: Time
##############

# TIER 1 TASK: Make sure ships have time to reach destination within time horizon.
# STATUS: V&V
# 36
def const_time_to_reach_m(model, j, m, v, t):
    if j == m or t < num_T - model.c_nnv[j,m,v]:
        return pyo.Constraint.Skip  # Skip constraint when j equals j_prime0
    return model.y_ship_out[j, m, v, t] == 0
model.const_time_to_reach_m = pyo.Constraint(model.J, model.M, model.V, model.T, rule=const_time_to_reach_m)

# TIER 1 TASK: Make sure arrive before they depart.
# STATUS: V&V
# 37
def const_ship_timing(model, j, v):
    return (
        sum((t+model.c_nnv[j_prime,j,v]+1)* model.y_ship_out[j_prime,j, v, t]
            for j_prime in model.J_0 if j != j_prime
            for t in model.T_0 if t >= model.c_nnv[j_prime, j, v])
            <=
            sum(
                t * model.y_ship_out[j, m, v, t]
                for m in model.M if j != m
                for t in model.T if t <= num_T -model.c_nnv[j, m, v]))
model.const_ship_timing = pyo.Constraint(model.J, model.V, rule=const_ship_timing)



# ##############
# # ENTITY: Supply Snchronization
# ##############
# TIER 1 TASK: Ship Reach Destination
# STATUS: V&V
# 38
def const_reach_destination(model, k):
    return (sum(model.x_ship_out[j,k,v,t] for j in model.J for v in model.V for t in model.T)
            == sum(model.a_i[i] for i in model.I))
model.const_reach_destination = pyo.Constraint(model.K, rule=const_reach_destination)

# TIER 1 TASK: Overall supply balance
# STATUS: V&V
# 39
def const_flow_balance(model, j):
    return (sum(model.x_rail[i,j,t] for i in model.I for t in model.T)
            + sum(model.x_ship_out[j_prime,j,v,t] for j_prime in model.J if j != j_prime for v in  model.V for t in model.T)
            == sum(model.x_ship_out[j,m,v,t] for m in model.M if m != j for v in model.V for t in model.T))
model.const_flow_balance = pyo.Constraint(model.J, rule=const_flow_balance)

# TIER 1 TASK: Time supply balance
# STATUS: V&V
# 40
def const_const_supply(model, j, t):
    return (sum(model.x_rail[i,j,t_prime] for i in model.I for t_prime in range(1,t+1))
            + sum(model.x_ship_out[j_prime,j,v,t_prime] for j_prime in model.J if j != j_prime for v in  model.V for t_prime in range(1,t) if t_prime + model.c_nnv[j_prime, j, v] + 1 <= t)
            <= sum(model.x_ship_out[j,m,v,t_prime] for m in model.M if m != j for v in model.V for t_prime in range(1,t+1)))
model.const_const_supply = pyo.Constraint(model.J, model.T, rule=const_const_supply)

# TIER 1 TASK: Make sure there is ship storage
# STATUS: V&V
def const_storage(model, j, t):
    return (   sum(                  model.x_rail[i,j,t_prime] for i in model.I for t_prime in range(1,t+1))
            +  sum(                  model.x_ship_out[j_prime,j,v,t_prime]
                   for j_prime in model.J_0 if j != j_prime
                   for v in  model.V
                   for t_prime in range(0,t) if t_prime + model.c_nnv[j_prime, j, v] <= t)
            -  sum(                  model.x_ship_out[j,m,v,t_prime] for m in model.M if m != j for v in model.V for t_prime in range(1,t+1))
            <= sum(model.u_ship[v] * model.y_ship_out[j_prime,j,v,t_prime]
                   for j_prime in model.J_0 if j != j_prime 
                   for v in model.V
                   for t_prime in range(0,t) if t_prime + model.c_nnv[j_prime, j, v] <= t)
            -  sum(model.u_ship[v] * model.y_ship_out[j,m,v,t_prime] for m in model.M if m != j for v in model.V for t_prime in range(1,t+1)))
model.const_storage = pyo.Constraint(model.J, model.T, rule=const_storage)


# TIER 1 TASK: Make sure there is ship storage
# STATUS: V&V
def const_ship_mono(model, j, v):
    return (sum(model.x_ship_out[j_prime,j,v,t] for j_prime in model.J_0 if j != j_prime  for t in model.T_0)
            <= sum(model.x_ship_out[j,m,v,t] for m in model.M if j != m for t in model.T))
model.const_ship_mono = pyo.Constraint(model.J,model.V, rule=const_ship_mono)

# Solve the model using Gurobi
solver = pyo.SolverFactory("gurobi")
# solver.options['Presolve'] = 0  # Use basic presolve (0 = off, 2 = aggressive)
solver.options['Presolve'] = 2  # Aggressive presolve
# # # Improve numerical stability
# # solver.options["NumericFocus"] = 3
# # solver.options["ScaleFlag"] = 1
# # solver.options["ObjScale"] = -1  # Helps with large objective values

# # # Select solver method
# # solver.options["Method"] = 2  # Use Barrier instead of Dual Simplex

# # Create solver
# # solver = pyo.SolverFactory('scip')

# # # # Set MIP gap to 1% (0.01)
# # # solver.options['limits/gap'] = 0.01
# # solver = pyo.SolverFactory('mosek')

# # # Set relative optimality gap to 1%
results = solver.solve(model, tee=True)



# Function to extract nonzero values and save to CSV
def export_variable_to_csv(var, filename):
    data = []
    for index in var:
        value = var[index].value
        if value is not None and value > 0:  # Filter out zero values
            data.append((*index, value))  # Unpack index tuple and append value

    if data:
        # Create DataFrame
        columns = [f"dim_{i+1}" for i in range(len(data[0]) - 1)] + ["value"]
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(filename, index=False)
        print(f"Exported {len(df)} nonzero entries to {filename}")
    else:
        print(f"No nonzero values to export for {filename}")


# Export each variable to a separate CSV file
export_variable_to_csv(model.x_rail, "x_rail.csv")
export_variable_to_csv(model.y_rail, "y_rail.csv")
export_variable_to_csv(model.x_ship_out, "x_ship_out.csv")
export_variable_to_csv(model.y_ship_out, "y_ship_out.csv")
print(num_T)