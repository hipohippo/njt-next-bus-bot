from telegram import Update, BotCommand
from telegram.ext import ContextTypes

from hipo_telegram_bot_common.util import restricted
from njt_next_bus_bot.bus_api.bus_and_stop import Stop, format_bus_message
from njt_next_bus_bot.bus_api.bus_api import next_bus_job


async def init_cmd(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.setMyCommands([BotCommand("/ny", "NYC Next Bus"), BotCommand("/nj", "NJ Next Bus")])


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
