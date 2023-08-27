import logging
import sys

from telegram.ext import CommandHandler, Application

from hipo_telegram_bot_common.bot_config.bot_config_parser import parse_from_ini
from hipo_telegram_bot_common.bot_factory import BotBuilder
from hipo_telegram_bot_common.common_handler import heart_beat_job
from njt_next_bus_bot.bot_handler import next_bus_handler, next_bus_pabt_handler, next_bus_lhny_handler, init_cmd, \
    lightrail_alert_handler, path_handler
from njt_next_bus_bot.bus_api.path_train_status import PathStation
from njt_next_bus_bot.njt_next_bus_bot_config import NJTNextBusBotConfig


def build_bot_app(bot_config_dict) -> Application:
    bot_config = NJTNextBusBotConfig(bot_config_dict)
    bot_app = (
        BotBuilder(bot_config_dict["bot_token"], bot_config)
        .add_handlers(
            [
                CommandHandler("next", next_bus_handler),
                CommandHandler("nj", next_bus_pabt_handler),
                CommandHandler("ny", next_bus_lhny_handler),
                CommandHandler("lr", lightrail_alert_handler),
                CommandHandler(set(PathStation.get_station_map().keys()), path_handler)
            ]
        )
        .add_onetime_jobs([(init_cmd, {"when": 2})])
        .add_repeating_jobs([(heart_beat_job, {"first": 5, "interval": 3 * 3600})])
        .build()
    )
    return bot_app


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    bot_config_file = sys.argv[1]
    bot_config_dict = parse_from_ini(bot_config_file)
    bot_app = build_bot_app(bot_config_dict)
    bot_app.run_polling()
