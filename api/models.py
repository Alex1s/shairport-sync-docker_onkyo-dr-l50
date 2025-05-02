from enum import Enum
from typing import List

from fastapi import Query
from pydantic import BaseModel, NonNegativeInt


class Power(str, Enum):
    OFF = "off"
    ON = "on"

class Input(str, Enum):
    TAPE_1 = "tape_1"
    PHONO = "phono"

class InputsModel(BaseModel):
    inputs: List[str]

class InputModel(BaseModel):
    input: Input

class PowerModel(BaseModel):
    power: Power

class VolumeModel(BaseModel):
    volume: float = Query(ge=0, le=1)

class OnkyoVolumeModel(BaseModel):
    volume: NonNegativeInt

class MuteModel(BaseModel):
    mute: bool
