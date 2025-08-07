import asyncio
import contextlib
import time
import logging
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_browser_and_tab, transfer_prompt
from pydoll.browser.tab import Tab

MISTRAL_URL: str = "https://chat.mistral.ai/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'button[type="submit"]'
TEXTAREA_CSS_SELECTOR: str = 'textarea[name="message.text"]'
ANSWER_CSS_SELECTOR: str = "div.prose"
SCROLL_DOWN_CSS_SELECTOR: str = 'button.disabled\\:pointer-auto[type="button"]'


async def check_if_chat_loaded(tab: Tab) -> bool:
    try:
        button = await tab.find(css_selector=SUBMIT_CSS_SELECTOR, timeout=5, raise_exc=False)
    except Exception as e:
        logging.warning("Can't find submit button in chat interface. Maybe it's not loaded yet.")
        return False
    return button is not None


async def scroll_to_bottom(tab: Tab) -> None:
    buttons = await tab.query(css_selector=SCROLL_DOWN_CSS_SELECTOR)
    for button in buttons[::-1]:
        parent_div = await button.find(xpath="..")
        if parent_div and await parent_div.tag_name == "div":
            await button.click()
            return


async def initialize_tab(config: Config):
    logging.info("Initializing browser for Mistral...")
    browser, tab = await create_browser_and_tab(config)
    await tab.go_to(MISTRAL_URL)

    while not await check_if_chat_loaded(tab):
        logging.info("Waiting for chat interface to load...")
        await asyncio.sleep(5)
    logging.info("Browser initialized")
    return browser, tab


async def send_request_and_get_response(tab: Tab, message: str):
    logging.debug("Send request to chatbot interface")
    textarea = await tab.find(css_selector=TEXTAREA_CSS_SELECTOR, timeout=10)
    await transfer_prompt(tab, message, textarea)
    await tab.find(css_selector=SUBMIT_CSS_SELECTOR, timeout=TIMEOUT_SECONDS)
    submit_button = await tab.find(css_selector=SUBMIT_CSS_SELECTOR)
    logging.debug("Push submit button")
    await submit_button.click()

    # Wait a little time to avoid early fail.
    await asyncio.sleep(1)

    # Wait for submit button to be available. It means answer is finished.
    await tab.find(css_selector=SUBMIT_CSS_SELECTOR, timeout=TIMEOUT_SECONDS)

    message_bubbles = await tab.query(css_selector=ANSWER_CSS_SELECTOR)
    if not message_bubbles:
        logging.warning("No message found.")
        return ""
    last_message_bubble = message_bubbles[-1]
    html = last_message_bubble.outer_html
    clean_message = clean_chat_answer(html)
    logging.debug(f"Clean message ends with: {clean_message[-100:]}")
    # await scroll_to_bottom(tab)
    return clean_message


def clean_chat_answer(html: str) -> str:
    """
    Find all DIVs containing code and remove unecessary decorations."
    """
    logging.debug("Clean chat answer")
    soup = BeautifulSoup(html, "html.parser")
    no_prose_divs = soup.find_all("div", class_="sticky")
    for div in no_prose_divs:
        if isinstance(div, Tag):
            div.clear()

    code_tags = soup.find_all("code")
    for code_tag in code_tags:
        code_tag.insert_before("```\n")
        code_tag.insert_after("\n```\n")
    return soup.get_text().strip()


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
