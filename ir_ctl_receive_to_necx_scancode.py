#!/usr/bin/env python3
import sys

LEADING_PULSE = 9000
LEADING_SPACE = -4500
BIT_PULSE = 562.5
BIT_SPACE_ONE = -1687.5
BIT_SPACE_ZERO = -562.5

TOLERANCE = 0.40


def read_file(file_name: str) -> str:
    """Reads the entire content of the file and returns it as a string, asserting no newlines."""
    with open(file_name, 'r') as file:
        content = file.read().strip()  # Read entire file and strip leading/trailing whitespace
    
    # Assert that there are no newlines in the content
    assert '\n' not in content, "The file contains newline characters, which is not allowed."
    
    return content

def parse_times(numbers_str: str) -> [int]:
    """Parses a string of space-separated numbers into a list of integers."""
    return list(map(int, numbers_str.split()))

def print_times(signal: [int]) -> None:
    """
    Prints the raw signal with two integers per line.
    """
    for i in range(0, len(signal), 2):
        # Print two integers per line
        print(f"{signal[i]} {signal[i+1]}")

def is_within_tolerance(actual: float, expected: float) -> bool:
    lower_bound = expected * (1 - TOLERANCE)
    upper_bound = expected * (1 + TOLERANCE)
    if lower_bound <= upper_bound:
        return lower_bound <= actual <= upper_bound
    else:
        return upper_bound <= actual <= lower_bound

def parse_signal(signal: [int]) -> list[int]:
    """
    Parses the signal and returns a list of bits (0 or 1).
    Uses assertions to check the validity of the signal.
    """
    bit_values = []

    # Step 1: Check the leading pulse
    assert is_within_tolerance(signal[0], LEADING_PULSE), f"Invalid leading pulse: expected {LEADING_PULSE} but got {signal[0]}"

    # Step 2: Check the leading space
    assert is_within_tolerance(signal[1], LEADING_SPACE), f"Invalid leading space: expected {LEADING_SPACE} but got {signal[1]}"

    # Step 3: Parse the 32 bits
    signal_bits = signal[2:]
    assert len(signal_bits) >= 64
    for i in range(0, 64, 2):  # Each bit has a pulse (index i) and a space (index i+1)
        bit_pulse = signal_bits[i]
        bit_space = signal_bits[i + 1]

        # Check if bit pulse is valid
        assert is_within_tolerance(bit_pulse, BIT_PULSE), f"Invalid bit pulse: expected {BIT_PULSE} but got {bit_pulse}"

        # Check the space corresponding to the bit
        if is_within_tolerance(bit_space, BIT_SPACE_ONE):
            bit_values.append(1)  # It's a 1
        elif is_within_tolerance(bit_space, BIT_SPACE_ZERO):
            bit_values.append(0)  # It's a 0
        else:
            assert False, f"Invalid bit space at index {i+1}: {bit_space}"

    return bit_values

def print_signal(bits: [int]) -> None:
    """
    Prints the signal (32-bit array) in packs of 8 bits per line.
    """
    byte_strings = []
    for i in range(0, len(bits), 8):
        # Print 8 bits per line
        byte_strings.append(''.join(map(str, bits[i:i+8])))
    print(" ".join(byte_strings))

def signal_to_bytes(bits: [int]) -> [int]:
    """
    Converts a list of 32 bits into a list of 4 bytes, where each byte is represented 
    as an integer. The least significant bit (LSB) is the first bit of each byte.
    """
    # Ensure the input is exactly 32 bits
    assert len(bits) == 32, f"Input signal must be 32 bits long but is {len(bits)} bits long"
    
    # Prepare an empty list to hold the 4 bytes
    bytes_list = []
    
    # Split the 32-bit array into 4 bytes (8 bits each)
    for i in range(0, 32, 8):
        # Take a slice of 8 bits, reverse them, and convert to an integer byte
        byte_bits = bits[i:i+8][::-1]  # Reverse the bits to make LSB first
        byte = sum(b << (7 - j) for j, b in enumerate(byte_bits))  # Convert bits to byte
        bytes_list.append(byte)
    
    return bytes_list

def print_hex_list(lst):
    print(" ".join([f"0x{num:02x}" for num in lst]))  # Prints without '0x' prefix and padded to 2 digits

def signal_bytes_to_scancode(signal_bytes: [int]) -> int:
    """
    3.9. nec-x (RC_PROTO_NECX)
    Extended nec has a 16 bit address and a 8 bit command. This is encoded as a 24 bit value as you would expect, with the lower 8 bits the command and the upper 16 bits the address.
    """
    assert len(signal_bytes) == 4
    assert signal_bytes[2] == 0xFF - signal_bytes[3]

    command = signal_bytes[2]
    # address = signal_bytes[0] | (signal_bytes[1] << 8)
    address = signal_bytes[1] | (signal_bytes[0] << 8)
    scancode = command | address << 8

    print(f"address=0x{address:04x} command=0x{command:02x} scancode=0x{scancode:06x}")

    return scancode
    

def main() -> None:
    """Main function to read the entire file, parse the numbers, and print the integer list."""
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    file_name = sys.argv[1]
    numbers_str = read_file(file_name)
    numbers = parse_times(numbers_str)
    print_times(numbers)
    signal = parse_signal(numbers)
    print(signal)
    print_signal(signal)
    signal_bytes = signal_to_bytes(signal)
    print_hex_list(signal_bytes)
    scancode = signal_bytes_to_scancode(signal_bytes)

    print(f'0x{scancode:06x}')


if __name__ == '__main__':
    main()