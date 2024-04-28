from src import config as cfg
from src import simulation_functions as sim_f
from src import info_inout as iout

if __name__ == '__main__':
    prep_combs = sim_f.prepare_combinations(cfg.COMBINATION_ELEMENTS, cfg.ELEMENTS_EXCLUDED, cfg.BER)
    result_list = sim_f.run_processes(prep_combs, cfg.PROCESSES_NUMBER)
    result_list.sort(key=lambda x: x[0], reverse=False)
    iout.csv_write(result_list, cfg.RESULT_FILE_PATH)
    lst = iout.csv_read(cfg.RESULT_FILE_PATH)
#    for i in range(len(lst)):
#        print(lst[i])



