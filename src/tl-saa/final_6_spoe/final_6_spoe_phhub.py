
import final_6_spoe

from mpisppy.spin_the_wheel import WheelSpinner
from mpisppy.utils import config
import mpisppy.utils.cfg_vanilla as vanilla
from mpisppy.cylinders.hub import LShapedHub
from mpisppy.opt.lshaped import LShapedMethod


def _parse_args():
    cfg = config.Config()
    cfg.num_scens_required()
    cfg.popular_args()
    cfg.two_sided_args()
    cfg.xhatlshaped_args()
    cfg.xhatlooper_args()
    cfg.ph_args()
    # cfg.subgradient_args()
    cfg.fwph_args()
    cfg.lagrangian_args()
    # cfg.subgradient_bounder_args()
    cfg.xhatshuffle_args()
    cfg.slammax_args()
    cfg.cross_scenario_cuts_args()
    # cfg.reduced_costs_args()
    cfg.parse_command_line("ts_cylinders")
    return cfg


def main():
    cfg = _parse_args()
    num_scen = cfg.num_scens
    scenario_creator = final_6_spoe.scenario_creator
    scenario_denouement = final_6_spoe.scenario_denouement
    all_scenario_names = [f"scen{sn}" for sn in range(num_scen)]
    print(all_scenario_names)
    scenario_creator_kwargs = {
        "divisions_per_day": 3,
        "replication": 0
    }
    
    # Things needed for vanilla cylinders
    beans = (cfg, scenario_creator, scenario_denouement, all_scenario_names)

    # Options for the L-shaped method at the hub
    spo = None if cfg.max_solver_threads is None else {"threads": cfg.max_solver_threads}
    options = {
        "root_solver": cfg.solver_name,
        "sp_solver": cfg.solver_name,
        "sp_solver_options": spo,
        #"valid_eta_lb": {i: -432000 for i in all_scenario_names},
        "max_iter": cfg.max_iterations,
        "verbose": True,
        "root_scenarios":[all_scenario_names[0]]
   }
    ph_ext = None
    hub_dict = vanilla.ph_hub(*beans,
                                  scenario_creator_kwargs=scenario_creator_kwargs,
                                  ph_extensions=ph_ext,
                                  rho_setter = None)

    list_of_spoke_dict = list()

    # lagrangian_spoke = vanilla.lagrangian_spoke(*beans,
    #                                           scenario_creator_kwargs=scenario_creator_kwargs,
    #                                           rho_setter = None)
    # list_of_spoke_dict.append(lagrangian_spoke)

    # xhatshuffle_spoke = vanilla.xhatshuffle_spoke(*beans, scenario_creator_kwargs=scenario_creator_kwargs)
    # list_of_spoke_dict.append(xhatshuffle_spoke)




    WheelSpinner(hub_dict, list_of_spoke_dict).spin()


if __name__ == "__main__":
    main()
