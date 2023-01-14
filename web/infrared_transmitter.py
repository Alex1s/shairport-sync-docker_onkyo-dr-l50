import asyncio.subprocess
from logger import logger

from models import Power

IR_CTL_COMMAND = 'ir-ctl'

POWER_ON_MODE2 = '/mode2/power_on.mode2'
POWER_OFF_MODE2 = '/mode2/power_off.mode2'
VOLUME_UP_MODE2 = '/mode2/volume_up.mode2'
VOLUME_DOWN_MODE2 = '/mode2/volume_down.mode2'

POWER_GAP = 1  # 1 second
VOLUME_GAP = 70e-3  # 70ms


def airplay_volume_to_receiver_volume(airplay_volume: float) -> int:
    """
    We take a function of the form f(x) = c * a^x
    We require f(0) = 80, thus c=80
    We require f(-30) = .1, thus a≈1.24959611477344
    :param airplay_volume: airplay volume
    :return: onkyp volume
    """
    c = 80
    a = 1.24959611477344
    onkyo_volume = round(c * pow(a, airplay_volume))
    logger.warning(f'Volume converted: {airplay_volume} -> {onkyo_volume}')
    assert 0 <= onkyo_volume <= 80
    return onkyo_volume


async def ir_ctl(mode2_file: str, repeat: int = 0) -> None:
    send_args = [f'--send={mode2_file}'] * (repeat + 1)
    all_args = [IR_CTL_COMMAND, '--carrier=0'] + send_args
    logger.warning(f'Running ir-ctl: {all_args}')
    subprocess = await asyncio.subprocess.create_subprocess_exec(*all_args)
    result = await subprocess.wait()
    logger.warning(f'ir-ctl stdout: {subprocess.stdout}')
    logger.warning(f'ir-ctl stderr: {subprocess.stdout}')
    logger.warning(f'result: {result}')
    if result:
        raise RuntimeError(f'ir-ctl returned non-zero: {result}')


async def power(p: Power) -> None:
    if p == Power.ON:
        await power_on()
    else:
        await power_off()


async def power_on() -> None:
    await ir_ctl(POWER_ON_MODE2)
    await asyncio.sleep(POWER_GAP)


async def power_off() -> None:
    await ir_ctl(POWER_OFF_MODE2)
    await asyncio.sleep(POWER_GAP)


async def volume_up(num: int = 1) -> None:
    if num == 0:
        return
    await ir_ctl(VOLUME_UP_MODE2, num - 1)
    await asyncio.sleep(VOLUME_GAP)


async def volume_down(num: int = 1) -> None:
    if num == 0:
        return
    await ir_ctl(VOLUME_DOWN_MODE2, num - 1)
    await asyncio.sleep(VOLUME_GAP)
