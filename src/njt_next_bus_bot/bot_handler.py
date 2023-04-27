import logging
import xml.etree.ElementTree as ET
from typing import List

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from njt_next_bus_bot.bus_and_stop import Stop, NextBus, format_bus_message


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


async def next_bus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (not update.message) or (not update.message.text):
        ## await context.bot_data["bot_config"].reply_text(text="wrong command")
        return
    direction = update.message.text.split(" ")[1]
    if direction not in {"NY", "NJ"}:
        await update.message.reply_text(text="unable to recognize direction")
        return
    stop = {"NY": Stop.LHNY, "NJ": Stop.PABT}[direction]
    next_bus_list = await next_bus_job(stop)
    message = format_bus_message(next_bus_list, stop, direction)
    await update.message.reply_text(text=message, parse_mode="HTML")

async def next_bus_lhny_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_bus_list = await next_bus_job(Stop.LHNY)
    message = format_bus_message(next_bus_list, Stop.LHNY, "NY")
    await update.message.reply_text(text=message, parse_mode="HTML")

async def next_bus_pabt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_bus_list = await next_bus_job(Stop.PABT)
    message = format_bus_message(next_bus_list, Stop.LHNY, "NJ")
    await update.message.reply_text(text=message, parse_mode="HTML")

