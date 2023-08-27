from telegram import Update, BotCommand
from telegram.ext import ContextTypes

from hipo_telegram_bot_common.util import restricted
from njt_next_bus_bot.bus_api.bus_and_stop import Stop, format_bus_message
from njt_next_bus_bot.bus_api.bus_api import next_bus_job
from njt_next_bus_bot.bus_api.lightrail import get_hblr_alert
from njt_next_bus_bot.bus_api.path_train_status import html_format_path_status_output, get_train_status, PathStation
from njt_next_bus_bot.njt_next_bus_bot_config import NJTNextBusBotConfig


async def init_cmd(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.setMyCommands(
        [BotCommand("/ny", "NYC Next Bus"), BotCommand("/nj", "NJ Next Bus"), BotCommand("/lr", "Light Rail Alert")]
    )


@restricted
async def next_bus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (not update.message) or (not update.message.text):
        ## await context.bot_data["bot_config"].reply_text(text="wrong command")
        return
    direction = update.message.text.split(" ")[1]
    if direction not in {"NY", "NJ"}:
        await update.message.reply_text(text="unable to recognize direction")
        return
    stop = {"NY": Stop.LHNY, "NJ": Stop.PABT}[direction]
    next_bus_list = await next_bus_job(stop, context.bot_data["driver"], context.bot_data["driver_handle"])
    message = format_bus_message(next_bus_list, stop, direction)
    await update.message.reply_text(text=message, parse_mode="HTML")


async def next_bus_lhny_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_bus_list = await next_bus_job(Stop.PABT.LHNY, context.bot_data["driver"], context.bot_data["driver_handle"])
    message = format_bus_message(next_bus_list, Stop.LHNY, "NY")
    await update.message.reply_text(text=message, parse_mode="HTML")


async def next_bus_pabt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_config: NJTNextBusBotConfig = context.bot_data["bot_config"]
    next_bus_list = await next_bus_job(Stop.PABT, context.bot_data["bot_config"], context.bot_data["bot_config"])
    message = format_bus_message(next_bus_list, Stop.PABT, "NJ")
    await update.message.reply_text(text=message, parse_mode="HTML")


async def lightrail_alert_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_config: NJTNextBusBotConfig = context.bot_data["bot_config"]
    lightrail_alert = get_hblr_alert()
    await update.message.reply_text(lightrail_alert, parse_mode="HTML")
    return lightrail_alert


async def path_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_config: NJTNextBusBotConfig = context.bot_data["bot_config"]
    query = update.message.text[1:]
    station_map = PathStation.get_station_map()
    if not query in station_map.keys():
        await update.message.reply_text(f"unknown station name. choose from f{' '.join(station_map.keys())}")
        return

    path_train_status = html_format_path_status_output(get_train_status(station_map.get(query)))
    await update.message.reply_text(path_train_status, parse_mode="HTML")
