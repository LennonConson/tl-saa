import numpy as np
divisions_per_day = 2
num_V = 18



ship_travel_times = {}


m = 0.1                   # Mean travel experiances a 10% delay
CV = 0.1                   # 20% variability
distance =5845*1.852

vehicle_speeds = 44 # km/h (max speed)
vehicle_speeds_effective = vehicle_speeds* (24/divisions_per_day) # convert to current timeperiods

for run in range(1000):
    t_min = distance / vehicle_speeds_effective 
    mean_travel_time = t_min * (1 + m) # minimum possible time (ideal conditions)
    sigma = np.sqrt(np.log(CV**2 + 1))
    mu = np.log(mean_travel_time) - (sigma**2 / 2)
    ship_travel_times[run] = max(round(np.random.lognormal(mean=mu, sigma=sigma)),1)
    print(ship_travel_times[run])
import matplotlib.pyplot as plt

# Convert dictionary values to a sorted NumPy array
samples = np.array(list(ship_travel_times.values()))
samples_sorted = np.sort(samples)
cdf = np.arange(1, len(samples_sorted)+1) / len(samples_sorted)

# Plot CDF
plt.figure(figsize=(8, 5))
plt.plot(samples_sorted, cdf, marker='.', linestyle='none')
plt.title("CDF of Simulated Ship Travel Time")
plt.xlabel("Travel Time (time periods)")
plt.ylabel("Cumulative Probability")
plt.grid(True)
plt.show()
plt.savefig("cdf_plot.png", dpi=300)

print(t_min)