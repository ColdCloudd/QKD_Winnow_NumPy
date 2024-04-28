from src import config as cfg
from src import simulation_functions as sim_f


if __name__ == '__main__':
    prep_combs = sim_f.prepare_combinations(cfg.COMBINATION_ELEMENTS, cfg.ELEMENTS_EXCLUDED, cfg.BER)
    sim_f.run_processes(prep_combs, cfg.PROCESSES_COUNT)


