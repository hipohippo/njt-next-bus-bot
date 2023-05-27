import logging
from typing import List
from xml.etree import ElementTree as ET

import httpx

from njt_next_bus_bot.bus_api.bus_and_stop import Stop, NextBus


def parse_bus_xml(stop: Stop, xml_content: bytes) -> List[NextBus]:
    tree = ET.fromstring(xml_content)
    bus_info = []
    for i, node in enumerate(tree):
        try:
            if node.tag == "pre":
                next_bus = NextBus(
                    stop,
                    node.find("pt").text,
                    node.find("pu").text,
                    node.find("rn").text,
                    node.find("nextbusonroutetime").text,
                )
                bus_info.append(next_bus)
                logging.info(f"{stop}: processed node {i}")
            else:
                logging.info(f"{stop}: no bus found")
        except Exception as e:
            if node.find("nextbusonroutetime"):
                logging.error(f"{stop}: unable to process node {i} {e}, node: {node.find('nextbusonroutetime').text}")
            else:
                logging.error(f"{stop}: unable to process node {i} {e}")
    return bus_info


async def next_bus_job(stop: Stop) -> List[NextBus]:
    bus_info_response = await httpx.AsyncClient().get(
        f"https://mybusnow.njtransit.com/bustime/eta/getStopPredictionsETA.jsp?route=all&stop={stop.id}"
    )
    if bus_info_response.status_code != 200:
        logging.error(f"error requesting bus info {bus_info_response.status_code}")
        return []
    return parse_bus_xml(stop, bus_info_response.content)
