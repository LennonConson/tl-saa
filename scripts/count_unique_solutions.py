import pandas as pd
import seaborn as sns

# Path to your CSV file
csv_path = "data/results/phase1_lshaped_results.csv"

# Read the CSV file
df = pd.read_csv(csv_path)

# Define the columns that make up a solution
solution_cols = [
    "y_open[6]", "y_open[7]", "y_open[8]",
    "y_open[9]", "y_open[10]", "y_open[11]"
]

# Group by 'outload' and 'number_samples', count unique solutions
unique_counts = (
    df.groupby(['outload_key', 'num_samples'])[solution_cols]
    .apply(lambda x: x.drop_duplicates().shape[0])
    .reset_index(name='unique_solution_count')
)

print(unique_counts)
unique_counts.to_csv("/home/user/git/tl-saa/data/results/phase1_unique_solution_counts.csv", index=False)
