import asyncio.subprocess
import math

from logger import logger

from models import Power, Input

from const import MAX_VOLUME

IR_CTL_COMMAND = 'ir-ctl'

from scancodes import *

GAP = 50e-3  # 50ms


def airplay_volume_to_receiver_volume(airplay_volume: float) -> int:
    if airplay_volume < -30:
        onkyo_volume = 0
    else:
        onkyo_volume = round((30 + airplay_volume) * MAX_VOLUME / 30)
    logger.warning(f'Volume converted: {airplay_volume} -> {onkyo_volume}')
    assert 0 <= onkyo_volume <= MAX_VOLUME
    return onkyo_volume


async def ir_ctl(scancode: int, repeat: int = 0) -> None:
    send_args = [f'--scancode=necx:0x{scancode:x}'] * (repeat + 1)
    all_args = [IR_CTL_COMMAND, '--carrier=38222', f'--gap={math.ceil(GAP * 1e6)}'] + send_args
    logger.warning(f'Running ir-ctl: {all_args}')
    subprocess = await asyncio.subprocess.create_subprocess_exec(*all_args)
    result = await subprocess.wait()
    assert subprocess.stdout is None, f'ir-ctl stdout: {subprocess.stdout}'
    assert subprocess.stderr is None, f'ir-ctl stderr: {subprocess.stderr}'
    assert result == 0, f'ir-ctl result: {result}'


async def power(p: Power) -> None:
    if p == Power.ON:
        await power_on()
    else:
        await power_off()


async def power_on() -> None:
    await ir_ctl(KEY_POWER)
    await asyncio.sleep(GAP)


async def power_off() -> None:
    await ir_ctl(KEY_POWER)
    await asyncio.sleep(GAP)


async def volume_up(num: int = 1) -> None:
    if num == 0:
        return
    await ir_ctl(KEY_VOLUME_UP, num - 1)
    await asyncio.sleep(GAP)


async def volume_down(num: int = 1) -> None:
    if num == 0:
        return
    await ir_ctl(KEY_VOLUME_DOWN, num - 1)
    await asyncio.sleep(GAP)

async def input(input: Input) -> None:
    if input == Input.TAPE_1:
        await ir_ctl(KEY_INPUT_SELECTOR_TAPE_1)
    elif input == Input.PHONO:
        await ir_ctl(KEY_INPUT_SELECTOR_PHONO)
    else:
        raise ValueError(f"Invalid input: {input}")