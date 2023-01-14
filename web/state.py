from pydantic import BaseModel

from models import PowerModel, VolumeModel, Power


class State(BaseModel):
    power: PowerModel = PowerModel(power=Power.OFF)
    volume: VolumeModel = VolumeModel(volume=-144)


class GlobalState(BaseModel):
    expectation: State = State()
    reality: State = State()


state = GlobalState()
