import logging
import xml.etree.ElementTree as ET
from enum import unique, Enum
from typing import List

import httpx
import pandas as pd
from telegram import Update
from telegram.ext import ContextTypes


@unique
class Stop(int, Enum):
    LHNY = 21831  ## lincoln harbor toward new york
    LHNJ = 21830  ## lincoln harbor toward new jersey


class NextBus:
    def __init__(self, stop: Stop, predicted_time: str, predicted_unit: str, bus_number: str, bus_timestamp: str):
        ## pd.Timedelta("7 minutes").components.minutes
        # self.bus_timestamp = pd.to_datetime('today').normalize() + pd.Timestamp(bus_timestamp)
        # {"pt": 7, "pu": minutes"} or {"pt": "&nbsp;", "pu":"APPROACHING"}
        self.predicted_time = predicted_time
        self.predicted_unit = predicted_unit
        self.bus_number = bus_number
        self.bus_timestamp = bus_timestamp
        self.arrival_time_delta = pd.Timedelta(f"{predicted_time} {predicted_unit}")

    def to_text(self):
        return f"{self.bus_number}  {self.predicted_time}  {self.predicted_unit} @ {self.bus_timestamp}"


def parse_bus_xml(stop: Stop, xml_content: bytes) -> List[NextBus]:
    tree = ET.fromstring(xml_content)
    bus_info = []
    for node in tree:
        try:
            next_bus = NextBus(
                stop,
                node.find("pt").text,
                node.find("pu").text,
                node.find("rn").text,
                node.find("nextbusonroutetime").text,
            )
            bus_info.append(next_bus)
        except Exception as e:
            logging.error("unable to process node")
    return bus_info


async def next_bus_job() -> List[NextBus]:
    stop_id = Stop.LHNJ
    bus_info_response = await httpx.AsyncClient().get(
        f"https://mybusnow.njtransit.com/bustime/eta/getStopPredictionsETA.jsp?route=all&stop={stop_id}"
    )
    if bus_info_response.status_code != 200:
        logging.error(f"error requesting bus info {bus_info_response.status_code}")
        return []
    return parse_bus_xml(stop_id, bus_info_response.content)


async def next_bus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_bus_list = await next_bus_job()
    await update.message.reply_text(text="\n".join([bus.to_text() for bus in next_bus_list]))
