import csv
import os
import sys
import pickle

def create_feasibility_dict(csv_file=None):
    """
    Converts feasibility_results.csv into a dictionary with 
    keys: (scenario_name, replication, divisions_per_day)
    values: min_feasible_days
    """
    # If no file specified, try to find it
    if csv_file is None:
        # Check command line arguments first
        if len(sys.argv) > 1:
            csv_file = sys.argv[1]
        else:
            # Try common locations
            possible_paths = [
                "feasibility_results.csv",
                "/home/lennon/git/tl-saa/src/tl-saa/final_6_spoe/feasibility_results.csv",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "feasibility_results.csv")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    csv_file = path
                    break
            
            if csv_file is None:
                print("Error: Could not find feasibility_results.csv")
                print("Please specify the file path as a command line argument:")
                print("python convert_to_dictionary.py /path/to/feasibility_results.csv")
                return {}
    
    print(f"Reading CSV file: {csv_file}")
    result_dict = {}
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract the key components
                scenario_name = row['scenario_name']
                replication = int(row['replication'])
                divisions_per_day = int(float(row['divisions_per_day']))
                min_feasible_days = int(float(row['min_feasible_days']))
                
                # Create the 3-tuple key and add to dictionary
                key = (scenario_name, replication, divisions_per_day)
                result_dict[key] = min_feasible_days
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
        return {}
        
    return result_dict

if __name__ == "__main__":
    feasibility_dict = create_feasibility_dict()
    if feasibility_dict:
        pickle_file = "feasibility_dict.pkl"
        with open(pickle_file, "wb") as pf:
            pickle.dump(feasibility_dict, pf)
        print(f"Dictionary saved to {pickle_file}")
    if feasibility_dict:
        print(f"Dictionary created with {len(feasibility_dict)} entries.")
        
        # Print a few sample entries
        print("\nSample entries:")
        for i, (key, value) in enumerate(list(feasibility_dict.items())[:3]):
            print(f"Key: {key}, Value: {value}")
    else:
        print("Failed to create dictionary - check file path.")