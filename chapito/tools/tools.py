import os
import platform
import asyncio
import logging
import re
import pyperclip
import requests

from chapito.config import Config
from chapito.types import OsType

from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.browser.tab import Tab
from pydoll.elements.web_element import WebElement


def get_os() -> OsType:
    os_name = os.name
    if os_name == "nt":
        return OsType.WINDOWS
    if os_name != "posix":
        return OsType.UNKNOWN
    return OsType.MACOS if platform.system() == "Darwin" else OsType.LINUX


async def paste(tab: Tab, textarea: WebElement):
    logging.debug("Paste prompt")
    await textarea.click()
    if get_os() == OsType.MACOS:
        await tab.keyboard.down('Meta')
        await tab.keyboard.press('v')
        await tab.keyboard.up('Meta')
    else:
        await tab.keyboard.down('Control')
        await tab.keyboard.press('v')
        await tab.keyboard.up('Control')


async def transfer_prompt(tab: Tab, message: str, textarea: WebElement) -> None:
    logging.debug("Transfering prompt to chatbot interface")
    usePaste = True
    if usePaste:
        pyperclip.copy(message)
        await paste(tab, textarea)
    else:
        # Send message line by line
        for line in message.split("\n"):
            # Don't send "\t" to browser to avoid focus change.
            await textarea.type(line.replace("\t", "    "))
            # Don't send "\n" to browser to avoid early submition.
            await tab.keyboard.down('Shift')
            await tab.keyboard.press('Enter')
            await tab.keyboard.up('Shift')
    await asyncio.sleep(0.5)
    logging.debug("Prompt transfered")


async def create_browser_and_tab(config: Config) -> tuple[Chrome, Tab]:
    options = ChromiumOptions()
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.user_agent = config.browser_user_agent
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=1")

    if config.use_browser_profile:
        browser_profile_path = os.path.abspath(config.browser_profile_path)
        os.makedirs(browser_profile_path, exist_ok=True)
        options.user_data_dir = browser_profile_path

    browser = Chrome(options=options)
    tab = await browser.start()
    return browser, tab


def check_official_version(version: str) -> bool:
    try:
        official_version = get_last_version()
        if version == official_version:
            return True
        logging.info(f"Official version: {official_version}")
        logging.info("Please update to the latest version.")
        logging.info("More infos: https://github.com/Yajusta/Chapito")
        return False
    except Exception as e:
        logging.error(f"Error checking version: {e}")
        return False


def get_last_version() -> str:
    response = requests.get("https://raw.githubusercontent.com/Yajusta/Chapito/refs/heads/main/pyproject.toml")
    response.raise_for_status()
    if match := re.search(r'version\s*=\s*"([^"]+)"', response.text):
        return match[1]
    return "0.0.0"


def greeting(version: str) -> None:
    text = rf"""
  /██████  /██                           /██   /██
 /██__  ██| ██                          |__/  | ██
| ██  \__/| ███████   /██████   /██████  /██ /██████    /██████
| ██      | ██__  ██ |____  ██ /██__  ██| ██|_  ██_/   /██__  ██
| ██      | ██  \ ██  /███████| ██  \ ██| ██  | ██    | ██  \ ██
| ██    ██| ██  | ██ /██__  ██| ██  | ██| ██  | ██ /██| ██  | ██
|  ██████/| ██  | ██|  ███████| ███████/| ██  |  ████/|  ██████/
 \______/ |__/  |__/ \_______/| ██____/ |__/   \___/   \______/
                              | ██
                              | ██
                              |__/        Version {version}
"""

    print(text)
