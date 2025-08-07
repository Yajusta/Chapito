import configparser
import argparse
from enum import Enum
import logging
import os.path
from shutil import copy
import sys

from chapito.tools.log import setup_logging_verbosity
from chapito.types import Chatbot

SAMPLE_CONFIG_FILE: str = "config.ini.sample"
DEFAULT_CONFIG_PATH: str = "config.ini"
DEFAULT_USE_BROWSER_PROFILE: bool = True
DEFAULT_BROWSER_PROFILE_PATH: str = "browser_profile"
DEFAULT_BROWSER_USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_VERBOSITY: int = 1
DEFAULT_CHATBOT: Chatbot = Chatbot.GROK
DEFAULT_STREAM: bool = False

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5001


def create_config_file() -> None:
    copy(SAMPLE_CONFIG_FILE, DEFAULT_CONFIG_PATH)


class Config:
    config_path: str = DEFAULT_CONFIG_PATH
    use_browser_profile: bool = DEFAULT_USE_BROWSER_PROFILE
    browser_profile_path: str = DEFAULT_BROWSER_PROFILE_PATH
    browser_user_agent: str = DEFAULT_BROWSER_USER_AGENT
    verbosity: int = DEFAULT_VERBOSITY
    chatbot: Chatbot = DEFAULT_CHATBOT
    stream: bool = DEFAULT_STREAM
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    headless: bool = False

    def __init__(self):
        logging.debug("Initializing config...")
        if not os.path.isfile(DEFAULT_CONFIG_PATH):
            create_config_file()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--config", type=str, help="Path to the config file (default: config.ini)", default=DEFAULT_CONFIG_PATH
        )
        parser.add_argument("--chatbot", type=str, help="Chatbot to connect to (available: grok, mistral)")
        parser.add_argument("--stream", action="store_true", help="Send response as stream")
        parser.add_argument("--no-stream", action="store_true", help="Don't send response as stream")
        g = parser.add_mutually_exclusive_group()
        g.add_argument("--use-browser-profile", action="store_true", default=None, help="Use a browser profile")
        g.add_argument(
            "--no-use-browser-profile", action="store_false", dest="use_browser_profile", help="Don't use a browser profile"
        )
        parser.add_argument("--headless", action="store_true", help="Run in headless mode")
        parser.add_argument("--profile-path", type=str, help="Path to the browser profile")
        parser.add_argument("--user-agent", type=str, help="User agent to use")
        parser.add_argument("--verbosity", type=int, help="Verbosity level")
        parser.add_argument("--host", type=str, help="Host/IP to bind to")
        parser.add_argument("--port", type=int, help="Port to listen on")
        args = parser.parse_args()
        self.config_path = args.config or DEFAULT_CONFIG_PATH
        config = configparser.ConfigParser()
        config.read(self.config_path)

        self.verbosity = args.verbosity or config.getint("DEFAULT", "verbosity", fallback=DEFAULT_VERBOSITY)
        setup_logging_verbosity(self.verbosity)
        if args.stream and args.no_stream:
            logging.error("Flags `--stream` and `--no-stream` are exclusive.")
            sys.exit()

        self.stream = args.stream or config.getboolean("DEFAULT", "stream", fallback=DEFAULT_STREAM)
        if args.no_stream:
            self.stream = False
        if args.use_browser_profile is None:
            self.use_browser_profile = config.getboolean(
                "DEFAULT", "use_browser_profile", fallback=DEFAULT_USE_BROWSER_PROFILE
            )
        else:
            self.use_browser_profile = args.use_browser_profile
        self.browser_profile_path = args.profile_path or config.get(
            "DEFAULT", "browser_profile_path", fallback=DEFAULT_BROWSER_PROFILE_PATH
        )
        self.browser_user_agent = args.user_agent or config.get(
            "DEFAULT", "browser_user_agent", fallback=DEFAULT_BROWSER_USER_AGENT
        )
        chatbot_str = args.chatbot or config.get("DEFAULT", "chatbot", fallback=DEFAULT_CHATBOT)
        try:
            chatbot = Chatbot(chatbot_str)
        except ValueError as e:
            logging.error(f"Invalid chatbot specified: {chatbot_str}")
            chatbot = DEFAULT_CHATBOT

        self.chatbot = Chatbot(chatbot)

        self.host = args.host or config.get("DEFAULT", "host", fallback=DEFAULT_HOST)
        self.port = args.port or config.getint("DEFAULT", "port", fallback=DEFAULT_PORT)
        self.headless = args.headless or config.getboolean("DEFAULT", "headless", fallback=False)

        logging.debug(f"Config initialized: {self.__dict__}")
