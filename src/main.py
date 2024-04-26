from src import config as cfg
from src import simulation_functions as sim_f


if __name__ == '__main__':
    prep_combs = sim_f.prepare_combinations(cfg.combination_elements, cfg.elements_excluded)
    sim_f.run_processes(cfg.PROCESSES_COUNT, cfg.SIFTED_KEY_LENGTH, cfg.BER, cfg.TRIAL_NUMBER,
                        prep_combs, cfg.SHUFFLE_MODE)


