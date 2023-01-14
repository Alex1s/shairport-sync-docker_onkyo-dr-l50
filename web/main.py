import asyncio
import logging
import sys

from fastapi import FastAPI
from asyncio import Future

from logger import logger
from models import PowerModel, AirplayVolumeModel
from state import state
import infrared_transmitter as ir_tx


expectations_changed: Future = asyncio.get_event_loop().create_future()


async def fulfil_expectations():
    try:
        while True:
            logger.warning('Waiting for a change ...')
            await expectations_changed
            logger.warning('The long awaited change happened!')
            while True:
                # power is first priority
                if state.expectation.power != state.reality.power:
                    logger.warning(f'power difference detected: {state.expectation.power.power} != {state.reality.power.power}')
                    state.reality.power = state.expectation.power
                    await ir_tx.power(state.expectation.power.power)
                    continue

                # volume is second priority
                expected_onkyo_volume = ir_tx.airplay_volume_to_receiver_volume(state.expectation.volume.volume)
                if expected_onkyo_volume != state.reality.volume.volume:
                    logger.warning(f'volume difference detected: {state.expectation.volume.volume} != {state.reality.volume.volume}')

                    if expected_onkyo_volume > state.reality.volume.volume:
                        state.reality.volume.volume += 1
                        await ir_tx.volume_up()
                    else:
                        state.reality.volume.volume -= 1
                        await ir_tx.volume_down()
                    continue

                # we changed nothing, thus we can wait for a change
                break
    except Exception as e:
        logger.error('Task did not handle a exception:')
        logger.error(e)
        sys.exit(1)


expectation_fulfiler = asyncio.get_event_loop().create_task(fulfil_expectations())


def expectations_change() -> None:
    global expectations_changed
    logger.setLevel(logging.DEBUG)
    logger.warn('Expectations are changing.')
    expectations_changed.set_result(None)
    expectations_changed = asyncio.get_event_loop().create_future()


app = FastAPI(title="Onkyo DR L50")


@app.get("/power", tags=["power"])
async def get_power() -> PowerModel:
    return state.reality.power


@app.put("/power", tags=["power"])
async def put_volume(power: PowerModel):
    state.expectation.power = power
    expectations_change()


@app.get("/volume", tags=["volume"])
async def get_volume() -> AirplayVolumeModel:
    return state.reality.volume


@app.put("/volume", tags=["volume"])
async def put_volume(volume: AirplayVolumeModel):
    state.expectation.volume = volume
    expectations_change()
