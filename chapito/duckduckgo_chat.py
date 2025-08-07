import asyncio
import logging
import pyperclip
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_browser_and_tab, transfer_prompt
from pydoll.browser.tab import Tab

URL: str = "https://duck.ai/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'button[type="submit"][aria-label="Send"]'
ANSWER_XPATH: str = "//div[@heading]"


async def check_if_chat_loaded(tab: Tab) -> bool:
    try:
        button = await tab.find(css_selector=SUBMIT_CSS_SELECTOR, timeout=5, raise_exc=False)
    except Exception as e:
        logging.warning("Can't find submit button in chat interface. Maybe it's not loaded yet.")
        return False
    return button is not None


async def initialize_tab(config: Config):
    logging.info("Initializing browser for DuckDuckGo...")
    browser, tab = await create_browser_and_tab(config)
    await tab.go_to(URL)

    while not await check_if_chat_loaded(tab):
        logging.info("Waiting for chat interface to load...")
        await asyncio.sleep(5)
    logging.info("Browser initialized")
    return browser, tab


async def send_request_and_get_response(tab: Tab, message: str):
    logging.debug("Send request to chatbot interface")
    textarea = await tab.find(tag_name="textarea", timeout=10)
    await transfer_prompt(tab, message, textarea)
    await tab.find(css_selector=SUBMIT_CSS_SELECTOR, timeout=TIMEOUT_SECONDS)
    await asyncio.sleep(1)
    submit_buttons = await tab.query(css_selector=SUBMIT_CSS_SELECTOR)
    submit_button = submit_buttons[-1]
    logging.debug("Push submit button")
    await submit_button.click()

    # Wait a little time to avoid early fail.
    await asyncio.sleep(1)

    # Wait for submit button to be available. It means answer is finished.
    await tab.find(css_selector=SUBMIT_CSS_SELECTOR, timeout=TIMEOUT_SECONDS)

    message = ""
    remaining_attemps = 5
    while not message and remaining_attemps > 0:
        await asyncio.sleep(1)
        message = await get_answer_from_copy_button(tab)
        remaining_attemps -= 1

    if not message:
        logging.warning("No message found.")
        return ""
    clean_message = clean_chat_answer(message)
    logging.debug(f"Clean message ends with: {clean_message[-100:]}")
    return clean_message


async def get_answer_from_copy_button(tab: Tab) -> str:
    message_bubbles = await tab.query(xpath=ANSWER_XPATH)
    if not message_bubbles:
        logging.warning("No message found.")
        return ""
    last_message_bubble = message_bubbles[-1]
    copy_button = await last_message_bubble.find(xpath="//*[@data-copyairesponse='true']")
    try:
        await copy_button.click()
    except Exception as e:
        logging.warning("Error clicking copy button:", e)
        return ""
    return pyperclip.paste()


def clean_chat_answer(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


async def main():
    browser, tab = await initialize_tab(Config())
    try:
        while True:
            user_request = input("Ask something (or 'quit'): ")
            if user_request.lower() == "quit":
                break
            response = await send_request_and_get_response(tab, user_request)
            print("Answer:", response)
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
