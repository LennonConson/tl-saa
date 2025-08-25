
import military_transshipment_port_selection as mtps
import pickle

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
    cfg.fwph_args()
    cfg.parse_command_line("ts_cylinders")
    return cfg


def main():
    cfg = _parse_args()
    num_scen = cfg.num_scens
    replications = 0
    replication = 0
    num_samples = num_scen
    outload_key = 0
    with open("/home/user/git/tl-saa/data/outload_5_samples100.pkl", "rb") as f:
        all_outload = pickle.load(f)
    outload= all_outload[outload_key]
    all_scenario_names = [f"delay_scen{i}" for i in range(num_samples)]

    scenario_creator = mtps.scenario_creator
    scenario_denouement = mtps.scenario_denouement
    all_scenario_names = [f"delay_scen{sn}" for sn in range(num_scen)]
    scenario_creator_kwargs = {
        "divisions_per_day": 3,
        "outload": outload,
        "replication": replication,
        "max_days": 20
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
        "verbose": False,
        "root_scenarios":[all_scenario_names[len(all_scenario_names)//2]]
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

        # FWPH spoke
    
    # fw_spoke = vanilla.fwph_spoke(*beans, scenario_creator_kwargs=scenario_creator_kwargs)
    
    # xhatlshaped_spoke = vanilla.xhatlshaped_spoke(*beans, scenario_creator_kwargs=scenario_creator_kwargs)


    list_of_spoke_dict = list()
    # list_of_spoke_dict.append(fw_spoke)
    # list_of_spoke_dict.append(xhatlshaped_spoke)
    WheelSpinner(hub_dict, list_of_spoke_dict).spin()


if __name__ == "__main__":
    main()
