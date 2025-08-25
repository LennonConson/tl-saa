
import pyomo.environ as pyo
import mpisppy.utils.sputils as sputils

def scenario_creator(scenario_name):
    """ Create a scenario    
    Args:
        scenario_name (str):
            Name of the scenario to construct.
    """
    # Create the concrete model object
    model = pysp_instance_creation_callback(scenario_name)
    sputils.attach_root_node(model, model.FirstStageCost, [model.DevotedAcreage])    
    return model

def pysp_instance_creation_callback(scenario_name):
    # long function to create the entire model
    # scenario_name is a string (e.g. 'scen0', 'scen1', 'scen2')


    model = pyo.ConcreteModel(scenario_name)
    
    #
    # Sets
    #
    model.CROPS = pyo.Set(initialize=['WHEAT', 'CORN', 'SUGAR_BEETS'])

    #
    # Parameters
    #
    model.TOTAL_ACREAGE = 500.0
    model.PriceQuota = {'WHEAT':100000.0,'CORN':100000.0,'SUGAR_BEETS':6000.0}
    model.SubQuotaSellingPrice = {'WHEAT':170.0,'CORN':150.0,'SUGAR_BEETS':36.0}
    model.SuperQuotaSellingPrice = {'WHEAT':0.0,'CORN':0.0,'SUGAR_BEETS':10.0}
    model.CattleFeedRequirement = {'WHEAT':200.0,'CORN':240.0,'SUGAR_BEETS':0.0}
    model.PurchasePrice = {'WHEAT':238.0,'CORN':210.0,'SUGAR_BEETS':100000.0}
    model.PlantingCostPerAcre = {'WHEAT':150.0,'CORN':230.0,'SUGAR_BEETS':260.0}

    #
    # Stochastic Data
    #
    Yield = {}
    Yield['BelowAverageScenario'] = {'WHEAT':2.0,'CORN':2.4,'SUGAR_BEETS':16.0}
    Yield['AverageScenario'] = {'WHEAT':2.5,'CORN':3.0,'SUGAR_BEETS':20.0}
    Yield['AboveAverageScenario'] = {'WHEAT':3.0,'CORN':3.6,'SUGAR_BEETS':24.0}

    def Yield_init(m, cropname):
        if scenario_name == "scen0":
            return Yield['BelowAverageScenario'][cropname]
        elif scenario_name == "scen1":
            return Yield['AverageScenario'][cropname]
        elif scenario_name == "scen2":
            return Yield['AboveAverageScenario'][cropname]

    model.Yield = pyo.Param(model.CROPS,
                            within=pyo.NonNegativeReals,
                            initialize=Yield_init,
                            mutable=True)
    # Scenario name: scen2
    # Yield : Size=3, Index=CROPS, Domain=NonNegativeReals, Default=None, Mutable=True
    #     Key         : Value
    #            CORN :   3.6
    #     SUGAR_BEETS :  24.0
    #           WHEAT :   3.0

    # Variables
    #
    model.DevotedAcreage = pyo.Var(model.CROPS, bounds=(0.0, model.TOTAL_ACREAGE))
    model.QuantitySubQuotaSold = pyo.Var(model.CROPS, bounds=(0.0, None))
    model.QuantitySuperQuotaSold = pyo.Var(model.CROPS, bounds=(0.0, None))
    model.QuantityPurchased = pyo.Var(model.CROPS, bounds=(0.0, None))

    #
    # Constraints
    #
    def ConstrainTotalAcreage_rule(model):
        return pyo.sum_product(model.DevotedAcreage) <= model.TOTAL_ACREAGE
    model.ConstrainTotalAcreage = pyo.Constraint(rule=ConstrainTotalAcreage_rule)

    def EnforceCattleFeedRequirement_rule(model, i):
        return model.CattleFeedRequirement[i] <= (model.Yield[i] * model.DevotedAcreage[i]) + model.QuantityPurchased[i] - model.QuantitySubQuotaSold[i] - model.QuantitySuperQuotaSold[i]
    model.EnforceCattleFeedRequirement = pyo.Constraint(model.CROPS, rule=EnforceCattleFeedRequirement_rule)

    def LimitAmountSold_rule(model, i):
        return model.QuantitySubQuotaSold[i] + model.QuantitySuperQuotaSold[i] - (model.Yield[i] * model.DevotedAcreage[i]) <= 0.0
    model.LimitAmountSold = pyo.Constraint(model.CROPS, rule=LimitAmountSold_rule)

    def EnforceQuotas_rule(model, i):
        return (0.0, model.QuantitySubQuotaSold[i], model.PriceQuota[i])
    model.EnforceQuotas = pyo.Constraint(model.CROPS, rule=EnforceQuotas_rule)

    # Stage-specific cost computations;

    def ComputeFirstStageCost_rule(model):
        return pyo.sum_product(model.PlantingCostPerAcre, model.DevotedAcreage)
    model.FirstStageCost = pyo.Expression(rule=ComputeFirstStageCost_rule)

    def ComputeSecondStageCost_rule(model):
        expr = pyo.sum_product(model.PurchasePrice, model.QuantityPurchased)
        expr -= pyo.sum_product(model.SubQuotaSellingPrice, model.QuantitySubQuotaSold)
        expr -= pyo.sum_product(model.SuperQuotaSellingPrice, model.QuantitySuperQuotaSold)
        return expr
    model.SecondStageCost = pyo.Expression(rule=ComputeSecondStageCost_rule)

    def total_cost_rule(model):
        return model.FirstStageCost + model.SecondStageCost        
    model.Total_Cost_Objective = pyo.Objective(rule=total_cost_rule, sense=pyo.minimize)

    return model




#============================
def scenario_denouement(rank, scenario_name, scenario):
    print("HELLO")
    print("Rank:", rank)
    print("Scenario Name:", scenario_name)
    print("Scenario:", scenario)
