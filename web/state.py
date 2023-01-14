from pydantic import BaseModel

from models import PowerModel, AirplayVolumeModel, Power, OnkyoVolumeModel


class StateExpectation(BaseModel):
    power: PowerModel = PowerModel(power=Power.OFF)
    volume: AirplayVolumeModel = AirplayVolumeModel(volume=-144)


class StateReality(BaseModel):
    power: PowerModel = PowerModel(power=Power.OFF)
    volume: OnkyoVolumeModel = OnkyoVolumeModel(volume=0)


class GlobalState(BaseModel):
    expectation: StateExpectation = StateExpectation()
    reality: StateReality = StateReality()


state = GlobalState()
