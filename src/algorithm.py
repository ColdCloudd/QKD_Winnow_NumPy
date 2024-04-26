import numpy as np


def winnow(alice_bit_array: np.ndarray, bob_bit_array: np.ndarray, syndrome_power: int):
    block_length = 2 ** syndrome_power
    hash_matrix = calculate_Hamming_hash_function(syndrome_power)
    b_odd_parity_block_numbers = [
        int(i / block_length)
        for i in range(0, len(alice_bit_array), block_length)
        if block_parity_check(alice_bit_array[i:i + block_length]) !=
           block_parity_check(bob_bit_array[i:i + block_length])
    ]
    # print(b_odd_parity_block_numbers)

    alice_privacy_amp_1 = discard_bits_for_parity_check(alice_bit_array, syndrome_power)
    bob_privacy_amp_1 = discard_bits_for_parity_check(bob_bit_array, syndrome_power)
    # print(alice_privacy_amp_1)
    # print(bob_privacy_amp_1)

    block_length -= 1
    for i in range(0, len(alice_privacy_amp_1), block_length):
        if i / block_length in b_odd_parity_block_numbers:
            a_syndrome = calculate_syndrome(alice_privacy_amp_1[i:i + block_length], hash_matrix)
            b_syndrome = calculate_syndrome(bob_privacy_amp_1[i:i + block_length], hash_matrix)
            alice_privacy_amp_1[i:i + block_length] = correct_error(alice_privacy_amp_1[i:i + block_length],
                                                                    a_syndrome, b_syndrome)
    # print(alice_privacy_amp_1)
    # print(bob_privacy_amp_1)

    remaining_bits_number = block_length - syndrome_power
    array_length = len(alice_privacy_amp_1) - len(b_odd_parity_block_numbers) * syndrome_power
    alice_privacy_amp_2 = np.empty(array_length, dtype=np.uint8)
    bob_privacy_amp_2 = np.empty(array_length, dtype=np.uint8)
    discarded_bit_pos = [(2 ** i) - 1 for i in range(syndrome_power)]
    j = 0
    for i in range(0, len(alice_privacy_amp_1), block_length):
        if i / block_length in b_odd_parity_block_numbers:
            alice_privacy_amp_2[j:j + remaining_bits_number] = discard_bit_for_syndrome(
                alice_privacy_amp_1[i:i + block_length], discarded_bit_pos)
            bob_privacy_amp_2[j:j + remaining_bits_number] = discard_bit_for_syndrome(
                bob_privacy_amp_1[i:i + block_length], discarded_bit_pos)
            j += remaining_bits_number
        else:
            alice_privacy_amp_2[j:j + block_length] = alice_privacy_amp_1[i:i + block_length]
            bob_privacy_amp_2[j:j + block_length] = bob_privacy_amp_1[i:i + block_length]
            j += block_length
    # print(alice_privacy_amp_2)
    # print(bob_privacy_amp_2)
    return alice_privacy_amp_2, bob_privacy_amp_2


def correct_error(bit_block: np.ndarray, first_syndrome: np.ndarray, second_syndrome: np.ndarray) -> np.ndarray:
    difference_syndrome = first_syndrome ^ second_syndrome
    error_bit_position = -1
    error_bit_position += np.dot(difference_syndrome[:, 0], np.power(2, np.arange(difference_syndrome.shape[0])))
    if error_bit_position >= 0:
        bit_block[error_bit_position] = 1 - bit_block[error_bit_position]
    else:
        return bit_block
    return bit_block


def calculate_Hamming_hash_function(syndrome_power: int) -> np.ndarray:
    block_length = 2 ** syndrome_power - 1
    # Создание двумерного массива
    column_indices = np.arange(block_length, dtype=np.uint16)[:, np.newaxis]
    # Расчет массива, состоящего из степеней двойки
    row_powers_of_2 = 2 ** np.arange(syndrome_power, dtype=np.uint16)
    # Деление столбца на строку с округлением вниз с дальнейшим поэлементным mod 2
    hash_matrix = (column_indices + 1) // row_powers_of_2 % 2
    # Транспонирование матрицы
    return hash_matrix.T


def calculate_syndrome(bit_block: np.ndarray, hash_matrix: np.ndarray) -> np.ndarray:
    column_vector = np.array(bit_block)[:, np.newaxis]
    return np.dot(hash_matrix, column_vector) % 2


def block_parity_check(bit_block: np.ndarray) -> bool:
    return np.sum(bit_block) % 2 == 0


def discard_bits_for_parity_check(bit_array: np.ndarray, syndrome_power: int) -> np.ndarray:
    block_length = 2 ** syndrome_power
    # Разбиваем битовую строку на блоки
    blocks = bit_array.reshape(-1, block_length)
    # Выбираем все биты, кроме первого в каждом блоке
    valid_bits = blocks[:, 1:]
    # Объединяем выбранные биты в один массив
    return valid_bits.flatten()


def discard_bit_for_syndrome(bit_block: np.ndarray, discarded_bit_positions: list[int]) -> np.ndarray:
    return np.delete(bit_block, discarded_bit_positions)
