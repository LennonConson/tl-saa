mpiexec -np 2 python -u -m mpi4py final_6_spoe_lshapedhub.py --num-scens 50 --bundles-per-rank=0 --max-iterations=50 --solver-name=gurobi_persistent --rel-gap=0.0 --xhatlshaped --max-solver-threads=12 --verbose
# MPI Command Flags Explained
# ## MPI and Python flags:

# - **`mpiexec -np 2`**: Launches 2 parallel MPI processes
# - **`python -u`**: Runs Python with unbuffered output (prints appear immediately)
# - **`-m mpi4py`**: Loads the mpi4py module to enable MPI communication in Python

# ## L-shaped method configuration:

# - **`--num-scens 3`**: Sets the number of scenarios to 3
# - **`--bundles-per-rank=0`**: Disables scenario bundling (each scenario processed separately)
# - **`--max-iterations=50`**: Limits the L-shaped algorithm to 50 iterations
# - **`--solver-name=gurobi_persistent`**: Uses Gurobi solver with persistent interface
# - **`--rel-gap=0.0`**: Sets the convergence tolerance to 0 (exact solution)
# - **`--xhatlshaped`**: Uses the xhat consensus solution variant of L-shaped method
# - **`--max-solver-threads=1`**: Restricts each solver instance to use only one thread

# The script solves a lateral transhipment problem with 3 scenarios distributed across 2 MPI processes, using the L-shaped decomposition method with Gurobi as the solver.

# usage: ts_cylinders [-h] --num-scens INT [--max-iterations INT]
#                     [--time-limit INT] [--solver-log-dir STR]
#                     [--warmstart-subproblems] [--user-warmstart]
#                     [--solver-name STR] [--solver-options STR] [--seed INT]
#                     [--default-rho FLOAT] [--bundles-per-rank INT] [--verbose]
#                     [--display-progress] [--display-convergence-detail]
#                     [--max-solver-threads INT] [--intra-hub-conv-thresh FLOAT]
#                     [--trace-prefix STR] [--tee-rank0-solves]
#                     [--auxilliary STR] [--presolve] [--rounding-bias FLOAT]
#                     [--config-file STR] [--rel-gap FLOAT] [--abs-gap FLOAT]
#                     [--max-stalled-iters INT] [--xhatlshaped]
