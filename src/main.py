import logging
import sys

from telegram.ext import CommandHandler, Application

from hipo_telegram_bot_common.bot_config_parser import parse_from_ini
from hipo_telegram_bot_common.bot_factory import bot_factory
from hipo_telegram_bot_common.common_handler import heart_beat_job
from njt_next_bus_bot.bot_handler import next_bus_handler
from njt_next_bus_bot.local_test import get_config_from_local_dev
from njt_next_bus_bot.njt_next_bus_bot_config import NJTNextBusBotConfig


def build_and_start_bot(bot_config_dict) -> Application:
    bot_config = NJTNextBusBotConfig(bot_config_dict)
    bot_app = bot_factory(
        bot_config_dict["token"],
        bot_config,
        handlers=[CommandHandler("next", next_bus_handler)],
        repeating_jobs=[(heart_beat_job, {"first": 5, "inverval": 3 * 3600})],
        onetime_jobs=None,
    )
    bot_app.run_polling()
    return bot_app


def get_bot_config_dict(mode) -> dict:
    if mode == "PROD":
        bot_config_file = sys.argv[2]
        bot_config_dict = parse_from_ini(bot_config_file)
    else:
        bot_config_dict = get_config_from_local_dev()
    return bot_config_dict


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    bot_config_dict = get_bot_config_dict("PROD")
    bot_app = build_and_start_bot(bot_config_dict)
