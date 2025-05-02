from pydantic import BaseModel

from models import PowerModel, VolumeModel, Power, OnkyoVolumeModel, MuteModel, InputModel, Input


class StateExpectation(BaseModel):
    power: PowerModel = PowerModel(power=Power.OFF)
    volume: VolumeModel = VolumeModel(volume=0.25)
    mute: MuteModel = MuteModel(mute=False)
    input: InputModel = InputModel(input=Input.TAPE_1)


class StateReality(BaseModel):
    power: PowerModel = PowerModel(power=Power.OFF)
    volume: OnkyoVolumeModel = OnkyoVolumeModel(volume=0)
    input: InputModel = InputModel(input=Input.TAPE_1)


class GlobalState(BaseModel):
    expectation: StateExpectation = StateExpectation()
    reality: StateReality = StateReality()


state = GlobalState()
