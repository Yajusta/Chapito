import os
import platform
import time
from chapito.config import Config
from chapito.types import OsType
from selenium.webdriver.common.keys import Keys
import pyperclip
import logging
import requests
import re
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_os() -> OsType:
    os_name = os.name
    if os_name == "nt":
        return OsType.WINDOWS
    if os_name != "posix":
        return OsType.UNKNOWN
    return OsType.MACOS if platform.system() == "Darwin" else OsType.LINUX


def paste(textarea):
    logging.debug("Paste prompt")
    textarea.click()
    if get_os() == OsType.MACOS:
        textarea.send_keys(Keys.COMMAND, "v")
    else:
        textarea.send_keys(Keys.CONTROL, "v")


def transfer_prompt(message, textarea) -> None:
    logging.debug("Transfering prompt to chatbot interface")
    usePaste = True
    if usePaste:
        pyperclip.copy(message)
        paste(textarea)
    else:
        # Send message line by line
        for line in message.split("\n"):
            # Don't send "\t" to browser to avoid focus change.
            textarea.send_keys(line.replace("\t", "    "))
            # Don't send "\n" to browser to avoid early submition.
            textarea.send_keys(Keys.SHIFT, Keys.ENTER)
    time.sleep(0.5)
    logging.debug("Prompt transfered")


def create_driver(config: Config) -> webdriver.Chrome | webdriver.Firefox:
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-agent={config.browser_user_agent}")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    if config.use_browser_profile:
        browser_profile_path = os.path.abspath(config.browser_profile_path)
        os.makedirs(browser_profile_path, exist_ok=True)
        chrome_options.add_argument(f"user-data-dir={browser_profile_path}")

    driver = webdriver.Chrome(options=chrome_options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


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
