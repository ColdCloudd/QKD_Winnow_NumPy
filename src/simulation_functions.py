import os
import itertools
import time
import tqdm
import numpy as np
import multiprocessing
from src import config as cfg
from src import algorithm as alg
from src import info_output as iout
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


def run_processes(combinations: list, process_count: int = os.cpu_count()):
    start = time.time()
    with multiprocessing.Pool(process_count) as pool:
        pool.starmap_async(run_tests, combinations, callback=final_callback, error_callback=error_callback)
        pool.close()
        pool.join()
    end = time.time()
    print(f"TIME = {end - start}")


def final_callback(result):
    print("All runs completed successfully!")
    for i in range(len(result)):
        print(f"№ = {result[i][0]}, comb = {result[i][1]}, e0 = {result[i][2]}, "
              f"mean_e_f = {result[i][3]:.5f}, mean_η = {result[i][4]:.5f}")


def error_callback(error):
    print(f'Got an Error: {error}', flush=True)


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


def run_tests(combination: tuple[int], error_probability: float, trial_number: int):
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
    return trial_number, combination, error_probability, mean_final_error, mean_remaining_fraction



