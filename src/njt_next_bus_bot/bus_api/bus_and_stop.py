from enum import Enum
from typing import List

import numpy as np
import pandas as pd


class Stop(Enum):
    def __init__(self, stop_name: str, direction: str, id: int):
        self.stop_name: str = stop_name
        self.direction: str = direction
        self.id: int = id

    def __str__(self):
        return f"{self.name}, {self.id}"

    LHNY = "LH", "NY", 21831  ## lincoln harbor toward new york
    LHNJ = "LH", "NJ", 21830  ## lincoln harbor toward new jersey
    PABT = "PABT", "NJ", 21830  ## port authority bus terminal toward new jersey


class NextBus:
    def __init__(self, stop: Stop, predicted_time: str, predicted_unit: str, bus_number: str, bus_timestamp: str):
        """
        * {"pt": 7, "pu": minutes"}
        * {"pt": "&nbsp;", "pu":"APPROACHING"}
        * now() + "pt" may not equal to bus_timestamp, should use the latter one if possible
        :param stop:
        :param predicted_time:  <pt>
        :param predicted_unit:  <pu>
        :param bus_number:      <rn>
        :param bus_timestamp:   <nextbusonroutetime>
        """
        self.predicted_time = np.nan if not predicted_time.isnumeric() else int(predicted_time)
        self.predicted_unit = predicted_unit.lower().strip()
        self.bus_number = bus_number
        self.bus_timestamp = bus_timestamp
        if not np.isnan(self.predicted_time):
            self.departure_time = pd.Timestamp.now() + pd.Timedelta(f"{self.predicted_time} {self.predicted_unit}")
        elif self.predicted_unit.lower().strip() == "approaching":
            self.departure_time = pd.Timestamp.now()
        else:
            self.departure_time = pd.Timestamp(bus_timestamp)

        # the api only returns bus arrival info for NJLH, we need to adjust for PABT
        if stop == Stop.PABT:
            self.departure_time -= pd.Timedelta("16 min")
            self.predicted_time -= 16

    def to_html(self) -> str:
        return f"{self.bus_number}: <b>{self.predicted_time} {self.predicted_unit}</b> @ <b>{self.departure_time.strftime('%I:%M %p')}</b>"

    def __str__(self) -> str:
        return f"pt: {self.predicted_time}, pu: {self.predicted_unit}, bustime: {self.bus_timestamp}"


def format_bus_message(bus_list: List[NextBus], stop: Stop, direction: str) -> str:
    message = (f"To <b>{direction}</b> Stop # {stop}:\n") + (
        "\n".join([bus.to_html() for bus in bus_list if bus.departure_time >= pd.Timestamp.now()]) if bus_list else "No bus found"
    )
    return message
