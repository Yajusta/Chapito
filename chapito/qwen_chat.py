import asyncio
import logging
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_browser_and_tab, transfer_prompt
from pydoll.browser.tab import Tab

URL: str = "https://chat.qwen.ai/"
TIMEOUT_SECONDS: int = 120
QUESTION_XPATH: str = "//textarea[@id='chat-input']"
SUBMIT_CSS_SELECTOR: str = "#send-message-button"
SUBMIT_DISABLE_CSS_SELECTOR: str = "#send-message-button[disabled]"
ANSWER_XPATH: str = "//div[@id='response-content-container']"


async def check_if_chat_loaded(tab: Tab) -> bool:
    try:
        element = await tab.find(xpath=QUESTION_XPATH, timeout=5, raise_exc=False)
    except Exception as e:
        logging.warning("Can't find specific element in chat interface. Maybe it's not loaded yet.")
        return False
    return element is not None


async def initialize_tab(config: Config):
    logging.info("Initializing browser for Qwen...")
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
    await asyncio.sleep(3)

    # Wait for submit button to be available. It means answer is finished.
    await tab.find(css_selector=SUBMIT_DISABLE_CSS_SELECTOR, timeout=TIMEOUT_SECONDS)

    await asyncio.sleep(1)
    message_bubbles = await tab.query(xpath=ANSWER_XPATH)
    if not message_bubbles:
        logging.warning("No message found.")
        return ""
    last_message_bubble = message_bubbles[-1]
    html = last_message_bubble.outer_html
    clean_message = clean_chat_answer(html)
    logging.debug(f"Clean message ends with: {clean_message[-100:]}")
    return clean_message


def clean_chat_answer(html: str) -> str:
    """
    Find all DIVs containing code and remove unecessary decorations."
    """
    logging.debug("Clean chat answer")
    soup = BeautifulSoup(html, "html.parser")
    for div in soup.find_all("div"):
        if isinstance(div, Tag) and "style" in div.attrs and "display: none;" in div["style"]:
            div.clear()

    no_prose_divs = soup.find_all("div", class_="code-cntainer")
    for div in no_prose_divs:
        if isinstance(div, Tag):
            code_tags = div.find_all("div", class_="cm-content")
            div.clear()
            for code in code_tags:
                div.append(code)
                code.insert_before("\n```\n")
                code.insert_after("\n```\n")
    clean_answer = soup.get_text(separator="\n").strip()
    while "\n\n" in clean_answer:
        clean_answer = clean_answer.replace("\n\n", "\n")
    return clean_answer


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
