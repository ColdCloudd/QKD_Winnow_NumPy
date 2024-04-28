import random
import numpy as np


def generate_random_bit_array(length: int) -> np.ndarray:
    random_bit_array = np.random.randint(0, 2, size=length, dtype=np.uint8)
    return random_bit_array


def introduce_errors(bit_array: np.ndarray, initial_error_probability: float) -> np.ndarray:
    error_mask = np.random.rand(len(bit_array)) < initial_error_probability
    bit_array_with_errors = bit_array ^ error_mask.astype(np.uint8)  # XOR
    return bit_array_with_errors


def calculate_error_positions(alice_bit_array: np.ndarray, bob_bit_array: np.ndarray) -> np.ndarray:
    error_positions = alice_bit_array ^ bob_bit_array
    return error_positions


def trim_to_block_length(alice_bit_array: np.ndarray, bob_bit_array: np.ndarray, block_length: int):
    common_multiple = (len(alice_bit_array) // block_length) * block_length
    trimmed_alice_bit_array = alice_bit_array[:common_multiple]
    trimmed_bob_bit_array = bob_bit_array[:common_multiple]
    return trimmed_alice_bit_array, trimmed_bob_bit_array


# перемешивает биты по *ссылке*
def shuffle_bits(alice_bit_array: np.ndarray, bob_bit_array: np.ndarray, seed: int):
    np.random.seed(seed)
    np.random.shuffle(alice_bit_array)
    np.random.seed(seed)
    np.random.shuffle(bob_bit_array)
