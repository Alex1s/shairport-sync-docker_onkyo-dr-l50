from enum import Enum

from fastapi import Query
from pydantic import BaseModel


class Power(str, Enum):
    OFF = "OFF"
    ON = "ON"


class PowerModel(BaseModel):
    power: Power


class VolumeModel(BaseModel):
    volume: float = Query(ge=-144, le=0)
