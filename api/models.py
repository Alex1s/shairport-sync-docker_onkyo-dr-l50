from enum import Enum
from typing import List

from fastapi import Query
from pydantic import BaseModel

from const import MAX_VOLUME


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


class AirplayVolumeModel(BaseModel):
    volume: float = Query(ge=-144, le=0)


class OnkyoVolumeModel(BaseModel):
    volume: int = Query(ge=0, le=MAX_VOLUME)


class MuteModel(BaseModel):
    mute: bool
