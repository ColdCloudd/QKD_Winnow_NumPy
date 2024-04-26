import itertools
import numpy as np
import multiprocessing
from src import config as cfg
from src import algorithm as alg
from src import bitstring_operations as bso


def prepare_combinations(combination_elements, excluded_elements):
    cartesian_product = list(itertools.product(combination_elements, repeat=len(combination_elements)))
    prepared_combinations = cartesian_product.copy()
    for i in range(len(cartesian_product)):
        for j in range(len(excluded_elements)):
            if cartesian_product[i][j] == excluded_elements[j]:
                prepared_combinations.remove(cartesian_product[i])
                break
    return prepared_combinations


def run_trial(alice_bit_array: np.ndarray, bob_bit_array: np.ndarray, trial_combination, shuffle_bits: bool):
    syndrome_power = cfg.INITIAL_SYNDROME_POWER
    a_bit_array = alice_bit_array
    b_bit_array = bob_bit_array
    seed = 0
    # внешний цикл определяет размер блока, а внутренний - количество проходов
    for i in range(len(trial_combination)):
        for j in range(trial_combination[i]):
            a_bit_array, b_bit_array = bso.trim_to_block_length(a_bit_array, b_bit_array, pow(2, syndrome_power))
            a_bit_array, b_bit_array = alg.winnow(a_bit_array, b_bit_array, syndrome_power)
            if shuffle_bits:
                bso.shuffle_bits(a_bit_array, b_bit_array, seed)
                seed += 1
        syndrome_power += 1
    # iout.print_info(a_bit_array, b_bit_array, cfg.SIFTED_KEY_LENGTH)
    return a_bit_array, b_bit_array


def run_tests(initial_key_length: int, error_probability_list, trials_number: int,
              combinations, shuffle_bits: bool, process_number: int):
    for i in range(len(combinations)):
        for j in range(len(error_probability_list)):
            for k in range(trials_number):
                alice_bit_array = bso.generate_random_bit_array(initial_key_length)
                bob_bit_array = bso.introduce_errors(alice_bit_array, error_probability_list[j])
                run_trial(alice_bit_array, bob_bit_array, combinations[i], shuffle_bits)
        print(f"{process_number}-process = {i * 100 / len(combinations): .2f}%")


def run_processes(process_count: int, initial_key_length: int, error_probability_list, trials_number: int,
                  combinations, shuffle_bits: bool):
    process_combinations_number = len(combinations) // process_count
    last_process_combinations_number = len(combinations) % process_count
    process_combinations = []

    for i in range(process_count):
        process_combinations.append(combinations[i * process_combinations_number: (i + 1) * process_combinations_number])

    if last_process_combinations_number > 0:
        process_combinations[-1].extend(combinations[-last_process_combinations_number:])

    processes = [
        multiprocessing.Process(target=run_tests, args=(initial_key_length, error_probability_list, trials_number,
                                                        process_combinations[i], shuffle_bits, i)
                                )
        for i in range(0, process_count)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
