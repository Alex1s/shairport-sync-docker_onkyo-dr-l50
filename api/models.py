from enum import Enum

from fastapi import Query
from pydantic import BaseModel

from const import MAX_VOLUME


class Power(str, Enum):
    OFF = "OFF"
    ON = "ON"


class PowerModel(BaseModel):
    power: Power


class AirplayVolumeModel(BaseModel):
    volume: float = Query(ge=-144, le=0)


class OnkyoVolumeModel(BaseModel):
    volume: int = Query(ge=0, le=MAX_VOLUME)
