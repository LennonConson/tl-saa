import final_6_spoe


from mpisppy.opt.lshaped import LShapedMethod

from mpisppy.utils import config


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
    scenario_creator_kwargs = {
        "divisions_per_day": 3,
        "replication": 0
    }
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
    ls = LShapedMethod(
        options,
        all_scenario_names,
        scenario_creator,
        scenario_creator_kwargs = scenario_creator_kwargs
    )
    
    result = ls.lshaped_algorithm()
    
if __name__ == "__main__":
    main()