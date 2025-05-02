import asyncio
import logging
import sys

from fastapi import FastAPI
from asyncio import Future

from logger import logger
from models import PowerModel, VolumeModel, Power, MuteModel, InputModel, InputsModel, Input
from state import state
import infrared_transmitter as ir_tx
from const import MAX_VOLUME, MAX_VOLUME_PHYS


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
                    logger.warning(f'Changing power state: {state.reality.power.power} -> {state.expectation.power.power}')
                    state.reality.power = state.expectation.power
                    if state.expectation.power.power == Power.ON:
                        state.reality.volume.volume = 0
                        await ir_tx.power_on()
                        await ir_tx.volume_down(num=MAX_VOLUME_PHYS)  # reset to zero
                    else:
                        await ir_tx.power_off()

                    # after power on, always assure input
                    await ir_tx.input(state.expectation.input.input)
                    state.reality.input = state.expectation.input
                
                    continue
                
                # input is next priority
                if state.expectation.input != state.reality.input:
                    await ir_tx.input(state.expectation.input.input)
                    state.reality.input = state.expectation.input
                    continue

                # volume is second priority
                if state.expectation.mute.mute:
                    expected_onkyo_volume = 0
                else:
                    expected_onkyo_volume = round(state.expectation.volume.volume * MAX_VOLUME[state.expectation.input.input])
                if expected_onkyo_volume != state.reality.volume.volume:
                    logger.warning(f'volume difference detected: expectation({expected_onkyo_volume}) != reality({state.reality.volume.volume})')
                    if state.reality.power.power == Power.ON:
                        if expected_onkyo_volume > state.reality.volume.volume:
                            state.reality.volume.volume += 1
                            await ir_tx.volume_up()
                        else:
                            state.reality.volume.volume -= 1
                            await ir_tx.volume_down()
                        continue
                    else:
                        logger.warning('Not changing volume because the receiver is off')

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


app = FastAPI(title="Onkyo TX SV9041")


@app.get("/power", tags=["power"])
async def get_power() -> PowerModel:
    return state.expectation.power


@app.put("/power", tags=["power"])
async def put_power(power: PowerModel):
    state.expectation.power = power
    expectations_change()


@app.get("/volume", tags=["volume"])
async def get_volume() -> VolumeModel:
    return state.expectation.volume


@app.put("/volume", tags=["volume"])
async def put_volume(volume: VolumeModel):
    if volume.volume == -144:
        state.expectation.mute = MuteModel(mute=True)
    else:
        state.expectation.mute = MuteModel(mute=False)
        state.expectation.volume = volume
    expectations_change()


@app.get("/mute", tags=["volume"])
async def get_mute() -> MuteModel:
    return state.expectation.mute


@app.put("/mute", tags=["volume"])
async def put_mute(mute: MuteModel):
    state.expectation.mute = mute
    expectations_change()


@app.get("/input", tags=["input"])
async def get_input() -> InputModel:
    return state.expectation.input


@app.put("/input", tags=["input"])
async def put_input(input: InputModel):
    state.expectation.input = input
    expectations_change()


@app.get("/inputs", tags=["input"])
async def get_inputs() -> InputsModel:
    return InputsModel(inputs=[input for input in Input])