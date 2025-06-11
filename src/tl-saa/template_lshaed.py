import pyomo.environ as pyo
import mpisppy.utils.sputils as sputils
from mpisppy.opt.lshaped import LShapedMethod
import random
import multiprocessing

def make_scenario_creator(num_scenarios, theta):
    def scenario_creator(scenario_name):
        yields = [
            random.uniform(2, 3),
            random.uniform(2.4, 3.6),
            random.uniform(16, 24),
        ]
        model = build_model(yields, theta)
        sputils.attach_root_node(model, model.PLANTING_COST, [model.X])
        model._mpisppy_probability = 1.0 / num_scenarios
        return model
    return scenario_creator

def build_model(yields, theta):
    model = pyo.ConcreteModel()

    model.X = pyo.Var(["WHEAT", "CORN", "BEETS"], within=pyo.NonNegativeReals)
    model.Y = pyo.Var(["WHEAT", "CORN"], within=pyo.NonNegativeReals)
    model.W = pyo.Var(
        ["WHEAT", "CORN", "BEETS_FAVORABLE", "BEETS_UNFAVORABLE"],
        within=pyo.NonNegativeReals,
    )

    # Use theta values for planting costs
    model.PLANTING_COST = (
        theta[0] * model.X["WHEAT"] +
        theta[1] * model.X["CORN"] +
        theta[2] * model.X["BEETS"]
    )

    model.PURCHASE_COST = 238 * model.Y["WHEAT"] + 210 * model.Y["CORN"]
    model.SALES_REVENUE = (
        170 * model.W["WHEAT"] + 150 * model.W["CORN"]
        + 36 * model.W["BEETS_FAVORABLE"] + 10 * model.W["BEETS_UNFAVORABLE"]
    )
    model.OBJ = pyo.Objective(
        expr=model.PLANTING_COST + model.PURCHASE_COST - model.SALES_REVENUE,
        sense=pyo.minimize
    )

    model.CONSTR = pyo.ConstraintList()
    model.CONSTR.add(pyo.summation(model.X) <= 500)
    model.CONSTR.add(yields[0] * model.X["WHEAT"] + model.Y["WHEAT"] - model.W["WHEAT"] >= 200)
    model.CONSTR.add(yields[1] * model.X["CORN"] + model.Y["CORN"] - model.W["CORN"] >= 240)
    model.CONSTR.add(
        yields[2] * model.X["BEETS"] - model.W["BEETS_FAVORABLE"] - model.W["BEETS_UNFAVORABLE"] >= 0
    )
    model.W["BEETS_FAVORABLE"].setub(6000)

    return model


def _lshaped_worker(num_scenarios, theta, options, conn):
    """
    Module‐level helper: builds and runs the L‐shaped algorithm,
    then sends back (objective, termination condition) over the pipe.
    """
    # Rebuild everything inside the child process
    all_scenario_names = list(range(1, num_scenarios + 1))
    scenario_creator = make_scenario_creator(num_scenarios, theta)
    ls = LShapedMethod(options, all_scenario_names, scenario_creator)
    result = ls.lshaped_algorithm()
    obj = pyo.value(ls.root.obj)
    term = result['Solver'][0]['Termination condition']
    conn.send((obj, term))
    conn.close()

def run_lshaped(num_scenarios, theta, solve_time_limit):
    """
    Run the L‐shaped algorithm but kill it if it exceeds solve_time_limit seconds.
    Returns (objective_value, termination_condition).
    """
    options = {
        "root_solver": "gurobi",
        "sp_solver":   "gurobi"
    }

    # Set up a pipe so the child can send back its result
    parent_conn, child_conn = multiprocessing.Pipe()

    # Launch the worker
    p = multiprocessing.Process(
        target=_lshaped_worker,
        args=(num_scenarios, theta, options, child_conn),
    )
    p.start()

    # Wait up to solve_time_limit seconds
    p.join(timeout=solve_time_limit)
    if p.is_alive():
        # still running: kill it
        p.terminate()
        p.join()
        # no valid objective—up to you how to handle this
        return None, "time_limit_reached"

    # child exited in time: grab its return values
    if parent_conn.poll():
        obj, term = parent_conn.recv()
        return obj, term
    else:
        # child died without sending anything
        return None, "error_no_result"