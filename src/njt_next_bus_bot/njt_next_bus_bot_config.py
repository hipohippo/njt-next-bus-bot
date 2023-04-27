from configparser import SectionProxy
from typing import Union

from hipo_telegram_bot_common.bot_config import BotConfig


class NJTNextBusBotConfig(BotConfig):
    def __init__(self, bot_config_dict: Union[dict, SectionProxy]):
        super().__init__(
            int(bot_config_dict["heart_beat_chat"]), int(bot_config_dict["error_notify_chat"]), bot_name="NJT Next Bus Bot"
        )
