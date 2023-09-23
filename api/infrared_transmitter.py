import asyncio.subprocess
import math

from logger import logger

from models import Power

from const import MAX_VOLUME

IR_CTL_COMMAND = 'ir-ctl'

POWER_ON_MODE2 = '/mode2/power_on.mode2'
POWER_OFF_MODE2 = '/mode2/power_off.mode2'
VOLUME_UP_MODE2 = '/mode2/volume_up.mode2'
VOLUME_DOWN_MODE2 = '/mode2/volume_down.mode2'

GAP = 50e-3  # 50ms


def airplay_volume_to_receiver_volume(airplay_volume: float) -> int:
    if airplay_volume < -30:
        onkyo_volume = 0
    else:
        onkyo_volume = round((30 + airplay_volume) * MAX_VOLUME / 30)
    logger.warning(f'Volume converted: {airplay_volume} -> {onkyo_volume}')
    assert 0 <= onkyo_volume <= MAX_VOLUME
    return onkyo_volume


async def ir_ctl(mode2_file: str, repeat: int = 0) -> None:
    send_args = [f'--send={mode2_file}'] * (repeat + 1)
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
    await ir_ctl(POWER_ON_MODE2)
    await asyncio.sleep(GAP)


async def power_off() -> None:
#    await ir_ctl(POWER_OFF_MODE2)
    await ir_ctl(POWER_ON_MODE2)
    await asyncio.sleep(GAP)


async def volume_up(num: int = 1) -> None:
    if num == 0:
        return
    await ir_ctl(VOLUME_UP_MODE2, num - 1)
    await asyncio.sleep(GAP)


async def volume_down(num: int = 1) -> None:
    if num == 0:
        return
    await ir_ctl(VOLUME_DOWN_MODE2, num - 1)
    await asyncio.sleep(GAP)
