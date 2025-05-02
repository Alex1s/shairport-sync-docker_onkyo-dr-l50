from collections import defaultdict
from models import Input


MAX_VOLUME_PHYS = 60  # determins how often it will perform "volume down" steps on startup to calibrate to zero]

MAX_VOLUME = defaultdict(lambda: 10)
MAX_VOLUME[Input.TAPE_1] = 10
MAX_VOLUME[Input.PHONO] = 20