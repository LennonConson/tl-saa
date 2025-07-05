import numpy as np
from pyomo.environ import *
import csv
def add_coffee_house_point_qcp(existing_points, dim=10, solver="gurobi", tee=False):
    model = ConcreteModel()

    # Decision variables: coordinates of the new point and radius r
    model.I = RangeSet(0, dim - 1)
    model.x = Var(model.I, bounds=(0, 1))
    model.r = Var(bounds=(0, None))  # Radius to be maximized

    # Constraint: r^2 <= sum((x_i - p_i)^2)
    model.constraints = ConstraintList()
    for point in existing_points:
        model.constraints.add(
            model.r**2 <= sum((model.x[i] - point[i])**2 for i in model.I)
        )

    # Objective: maximize r
    model.obj = Objective(expr=model.r, sense=maximize)

    # Solve using Gurobi with QCP enabled
    opt = SolverFactory(solver)
    results = opt.solve(model, tee=tee)

    return np.array([value(model.x[i]) for i in model.I])

def generate_coffee_house_sequence(n_points, dim=3, solver="gurobi", tee=False):
    # Start from center of unit hypercube
    points = [np.full(dim, 0.5)]

    for _ in range(n_points - 1):
        new_point = add_coffee_house_point_qcp(np.array(points), dim=dim, solver=solver, tee=tee)
        points.append(new_point)

    return np.array(points)

# Run example
if __name__ == "__main__":
    DIM = 5
    N_POINTS = 200
    sequence = generate_coffee_house_sequence(n_points=N_POINTS, dim=DIM, tee=True)


# assume sequence is a NumPy array or list-of-lists
seq_list = sequence.tolist()   # if it’s an ndarray

with open("sequence.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(sequence.tolist())
