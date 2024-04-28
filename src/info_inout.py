import csv
import numpy as np
import matplotlib.pyplot as plt

from src import bit_array_operations as bso


def visualize_error_positions(error_positions: np.ndarray):
    plt.stem(range(len(error_positions)), error_positions, markerfmt='')
    plt.xlabel("Позиция бита")
    plt.ylabel("Наличие ошибки")
    plt.title("Ошибки в битовой строке")
    plt.show()


def block_print(bit_array: np.ndarray, block_length: int, comment: str):
    bitstring_with_spaces = ""
    for i in range(len(bit_array)):
        if i % block_length == 0 and i != 0:
            bitstring_with_spaces += ' '
        bitstring_with_spaces += str(bit_array[i])
    print(f"{comment}: {bitstring_with_spaces}")


def print_info(alice_bit_array: np.ndarray, bob_bit_array: np.ndarray, sifted_key_length: int):
    error_positions = bso.calculate_error_positions(alice_bit_array, bob_bit_array)
    number_of_errors = np.sum(error_positions, dtype=np.intc)
    print(f"Количество ошибок = {number_of_errors}, "
          f"Длина ключа = {len(alice_bit_array)}, "
          f"BER = {number_of_errors / len(alice_bit_array): .5f}, "
          f"η = {len(alice_bit_array) / sifted_key_length: .5f}")


def csv_write(data: list, path: str):
    try:
        with open(path, 'w') as f:
            writer = csv.writer(f, delimiter=';', lineterminator='\n')
            for row in data:
                writer.writerow(list(row))
    except Exception as e:
        print(f'Error occurred (csv_write): {e}', flush=True)


def csv_read(path: str) -> list:
    data = []
    try:
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f'Error occurred (csv_read): {e}', flush=True)
    return data
