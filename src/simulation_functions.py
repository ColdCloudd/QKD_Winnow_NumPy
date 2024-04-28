import os
import itertools
import time
import tqdm
import numpy as np
import multiprocessing
from src import config as cfg
from src import algorithm as alg
from src import info_inout as iout
from src import bit_array_operations as bso


def prepare_combinations(combination_elements: list[int], excluded_elements: list[list[int]], error_probabilities: list[float]) -> list:
    cartesian_product = list(itertools.product(combination_elements, repeat=len(combination_elements)))
    prepared_combinations = cartesian_product.copy()
    for i in range(len(cartesian_product)):
        for j in range(len(excluded_elements)):
            if cartesian_product[i][j] in excluded_elements[j]:
                prepared_combinations.remove(cartesian_product[i])
                break
    trial_number = 1
    prepared_combinations_with_ber = []
    for i in range(len(prepared_combinations)):
        for j in range(len(error_probabilities)):
            prepared_combinations_with_ber.append((prepared_combinations[i], error_probabilities[j], trial_number))
            trial_number += 1
    return prepared_combinations_with_ber


def run_processes(combinations: list, processes_number: int = os.cpu_count()):
    result_list_tqdm = []
    try:
        pool = multiprocessing.Pool(processes=processes_number)
        results = [pool.apply_async(func=run_tests, args=(*argument,), error_callback=error_callback) for argument in combinations]
        pool.close()

        for res in tqdm.tqdm(results, desc="PROGRESS", mininterval=1):
            result_list_tqdm.append(res.get())
    except Exception as e:
        print(f'Error occurred (run_processes): {e}', flush=True)
        print(f'The obtained results will be written to the file at the path ???')
        return result_list_tqdm
    return result_list_tqdm


def error_callback(error):
    print(f'Error occurred: {error}', flush=True)


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
    return a_bit_array, b_bit_array


def run_tests(combination: tuple[int], error_probability: float, serial_number: int):
    mean_final_error: float = 0
    mean_remaining_fraction: float = 0
    for i in range(cfg.TRIAL_NUMBER):
        alice_bit_array = bso.generate_random_bit_array(cfg.SIFTED_KEY_LENGTH)
        bob_bit_array = bso.introduce_errors(alice_bit_array, error_probability)
        a_bit_array, b_bit_array = run_trial(alice_bit_array, bob_bit_array, combination, cfg.SHUFFLE_MODE)

        number_of_errors = np.sum(bso.calculate_error_positions(a_bit_array, b_bit_array), dtype=np.uint32)
        mean_final_error += number_of_errors / len(a_bit_array)
        mean_remaining_fraction += len(a_bit_array) / cfg.SIFTED_KEY_LENGTH
    mean_final_error = mean_final_error / cfg.TRIAL_NUMBER
    mean_remaining_fraction = mean_remaining_fraction / cfg.TRIAL_NUMBER
    return serial_number, combination, error_probability, mean_final_error, mean_remaining_fraction



