#!/usr/bin/env python3
"""
Script to create an upset plot for y_open variables from results.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
from upsetplot import from_memberships, UpSet
import numpy as np

# Read the CSV file
df = pd.read_csv('/home/user/git/tl-saa/scripts/deterministic_optimal_results_best_case.csv')

# Select only the y_open columns
y_open_cols = ['y_open[7]', 'y_open[8]', 'y_open[9]', 'y_open[10]', 'y_open[11]', 'y_open[12]']
y_open_data = df[y_open_cols]

# Convert to boolean (1.0 -> True, 0.0 or -0.0 -> False)
# Note: handling -0.0 as False as well
y_open_bool = y_open_data.abs() > 0.5  # This handles 1.0 as True and 0.0/-0.0 as False

# Map original column names to port names
port_names = {
    'y_open[7]': 'Beaumont',
    'y_open[8]': 'Gulfport',
    'y_open[9]': 'Charleston',
    'y_open[10]': 'Jacksonville',
    'y_open[11]': 'Morehead City',
    'y_open[12]': 'Portsmouth'
}

# Create a list of sets for each scenario
memberships = []
for idx, row in y_open_bool.iterrows():
    # Get the names of columns where value is True
    active_sets = [port_names[col] for col, val in row.items() if val]
    memberships.append(active_sets)

# Create the upset plot data
upset_data = from_memberships(memberships)

# Create the upset plot
fig = plt.figure(figsize=(12, 8))
upset = UpSet(upset_data, subset_size='count', show_counts=True, sort_categories_by='input', show_percentages=False)
upset.style_subsets(present="Beaumont", facecolor="red")
upset.style_subsets(present="Charleston", facecolor="green")
upset.style_subsets(present="Gulfport", facecolor="blue")
upset.style_subsets(present="Jacksonville", facecolor="orange")
upset.style_subsets(present="Morehead City", facecolor="purple")
upset.style_subsets(present="Portsmouth", facecolor="brown")
       
            
upset.plot(fig=fig)

# Add title and labels
plt.suptitle('Best Case Outload — Port Opening Combinations', fontsize=16, y=0.95)

# Adjust layout and save
plt.tight_layout()
plt.savefig('/home/user/git/tl-saa/upset_plot.png', dpi=300, bbox_inches='tight')
plt.savefig('/home/user/git/tl-saa/upset_plot.pdf', bbox_inches='tight')

# Display some statistics
print("=== Upset Plot Statistics ===")
print(f"Total number of scenarios: {len(df)}")
print(f"Number of unique port combinations: {len(upset_data)}")
print()

# Show the most common combinations
print("Most common port opening combinations:")
top_combinations = upset_data.sort_values(ascending=False).head(10)
print(f"Data type of upset_data: {type(upset_data)}")
print(f"Index type: {type(upset_data.index)}")
print(f"Sample index entries: {upset_data.index[:3].tolist()}")

for i, (combination, count) in enumerate(top_combinations.items()):
    print(f"  Combination {i+1}: {combination} -> {count} scenarios")
    if i >= 5:  # Limit to first 5 for debugging
        break

print()
print("Individual port opening frequencies:")
for col in y_open_cols:
    port_num = col.replace('y_open[', '').replace(']', '')
    frequency = y_open_bool[col].sum()
    percentage = (frequency / len(df)) * 100
    print(f"  Port {port_num}: {frequency} scenarios ({percentage:.1f}%)")

plt.show()
