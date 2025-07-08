
import pyomo.environ as pyo
import numpy as np
import mpisppy.utils.sputils as sputils

# Use this random stream:
farmerstream = np.random.RandomState()

def scenario_creator(
    scenario_name, seedoffset=0):
    """ Create a scenario for the (scalable) farmer example.
    
    Args:
        scenario_name (str):
            Name of the scenario to construct.
        seedoffset (int): used by confidence interval code
    """
    # scenario_name has the form <str><int> e.g. scen12, foobar7
    # The digits are scraped off the right of scenario_name using regex then
    # converted mod 3 into one of the below avg./avg./above avg. scenarios
    scennum   = sputils.extract_num(scenario_name)
    basenames = ['BelowAverageScenario', 'AverageScenario', 'AboveAverageScenario']
    basenum   = scennum  % 3
    groupnum  = scennum // 3
    scenname  = basenames[basenum]+str(groupnum)

    # The RNG is seeded with the scenario number so that it is
    # reproducible when used with multiple threads.
    # NOTE: if you want to do replicates, you will need to pass a seed
    # as a kwarg to scenario_creator then use seed+scennum as the seed argument.
    farmerstream.seed(scennum+seedoffset)



    # Create the concrete model object
    model = pysp_instance_creation_callback(
        scenname
    )

    # Create the list of nodes associated with the scenario (for two stage,
    # there is only one node associated with the scenario--leaf nodes are
    # ignored).
    varlist = [model.DevotedAcreage]
    sputils.attach_root_node(model, model.FirstStageCost, varlist)    
    
    #Add the probability of the scenario
    model._mpisppy_probability = "uniform"
    return model

def pysp_instance_creation_callback(scenario_name):
    # long function to create the entire model
    # scenario_name is a string (e.g. ts0, ts1, ts2, etc.)
    # scengroupnum is the integer part of scenario_name
    # scenario_base_name is the string part of scenario_name
    # Returns a concrete model for the specified scenario

    # scenarios come in groups of three
    scengroupnum = sputils.extract_num(scenario_name)
    scenario_base_name = scenario_name.rstrip("0123456789")

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
        # yield as in "crop yield"
        crop_base_name = cropname.rstrip("0123456789")
        if scengroupnum != 0:
            return Yield[scenario_base_name][crop_base_name]+farmerstream.rand()
        else:
            return Yield[scenario_base_name][crop_base_name]

    model.Yield = pyo.Param(model.CROPS,
                            within=pyo.NonNegativeReals,
                            initialize=Yield_init,
                            mutable=True)

    #
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
