#!/usr/bin/env python3.11
import argparse
import sys
import logging

__LOGGER = logging.getLogger(__name__)


def necx_scancode_to_bit_array(scancode: int) -> [int]:
    first_byte = (scancode & 0xFF0000) >> 16
    second_byte = (scancode & 0xFF00) >> 8
    third_byte = scancode & 0xFF

    __LOGGER.debug(list(map(hex, [first_byte, second_byte, third_byte])))
    bits = []
    for byte in [first_byte, second_byte, third_byte]:
        for i in range(8):
            bits.append(byte & (1 << i))
    __LOGGER.debug(bits)

    bits = list(map(bool, bits))
    __LOGGER.debug(bits)

    bits += list(map(lambda x: not x, bits[-8:]))
    __LOGGER.debug(bits)

    return bits


def necx_scancode_to_mode2(scancode: int) -> str:
    logging.debug(hex(scancode))

    bits = necx_scancode_to_bit_array(scancode)

    res = f'''# Leader code (header)
pulse 9000  # AGC (automatic gain control) pulse
space 4500  # LP (long pause)'''

    for i in range(4):
        if i == 0:
            res += f'\n\n# first address byte: {hex((scancode & 0xFF0000) >> 16)}\n'
        elif i == 1:
            res += f'\n# second address byte: {hex((scancode & 0xFF00) >> 8)}\n'
        elif i == 2:
            res += f'\n# command address byte: {hex((scancode & 0xFF00) >> 8)}\n'
        elif i == 3:
            res += f'\n# command address byte (inverted)\n'

        for bit in bits[i * 8:i * 8 + 8]:
            res += 'pulse  562\n'  # actually 562.5, but no decimals allowed; thus we round the pulse timing down and
            # the space timing up
            if bit:
                res += f'space  1688  # {int(bit)}\n'  # actually 1687.5, but no decimals allowed; thus we round the
                # space timing up and the pulse timing down
            else:
                res += f'space 563  # {int(bit)}\n'  # actually 562.5, but no decimals allowed; thus we round the
                # space timing up and the pulse timing down

    res += '\n# stop bit\n'
    res += 'pulse  562\n'  # actually 562.5, but no decimals allowed; thus we round the pulse down so that it is a
    # bit faster ;)
    return res


def main() -> None:
    parser = argparse.ArgumentParser(description='Converts NECX (NEC extended) scancodes to mode2 format (pulse / '
                                                 'space in μs).', epilog=f'Example: {sys.argv[0]} 0xD26D04')
    parser.add_argument('scancode', metavar='scancode', type=lambda scancode_str: int(scancode_str, 0),
                        help='the necx scancode')
    args = parser.parse_args()

    if not (0 <= args.scancode < 2 ** 24):
        print(f'Scancode provided ({hex(args.scancode)}) is not a NECX scancode.', file=sys.stderr)
        exit(1)

    print(necx_scancode_to_mode2(args.scancode))


if __name__ == '__main__':
    main()
