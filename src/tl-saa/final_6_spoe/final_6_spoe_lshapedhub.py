
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
        "max_days": 16,
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
    
    # L-shaped hub
    hub_dict = {
        "hub_class": LShapedHub,
        "hub_kwargs": {
            "options": {
                "rel_gap": cfg.rel_gap,
                "abs_gap": cfg.abs_gap,
            },
        },
        "opt_class": LShapedMethod,
        "opt_kwargs": { # Args passed to LShapedMethod __init__
            "options": options,
            "all_scenario_names": all_scenario_names,
            "scenario_creator": scenario_creator,
            "scenario_creator_kwargs": scenario_creator_kwargs,
        },
    }

    
    xhatlshaped_spoke = vanilla.xhatlshaped_spoke(*beans, scenario_creator_kwargs=scenario_creator_kwargs)


    list_of_spoke_dict = list()
    list_of_spoke_dict.append(xhatlshaped_spoke)
    WheelSpinner(hub_dict, list_of_spoke_dict).spin()


if __name__ == "__main__":
    main()
