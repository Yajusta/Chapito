import logging
import time

from bs4 import BeautifulSoup, Tag
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt

URL: str = "https://gemini.google.com/app"
TIMEOUT_SECONDS: int = 1000
SUBMIT_CSS_SELECTOR: str = "button.submit"
STOP_CSS_SELECTOR: str = "div.stop-icon"
MICROPHONE_CSS_SELECTOR: str = "div.mic-button-container:not(.hidden)"
ANSWER_XPATH: str = "//message-content"


def check_if_chat_loaded(driver) -> bool:
    driver.implicitly_wait(5)
    try:
        button = driver.find_element(By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
    except Exception:
        logging.warning("Can't find submit button in chat interface. Maybe it's not loaded yet.")
        return False
    return button is not None


def initialize_driver(config: Config):
    logging.info("Initializing browser for Gemini...")
    driver = create_driver(config)
    driver.get(URL)

    while not check_if_chat_loaded(driver):
        logging.info("Waiting for chat interface to load...")
        time.sleep(5)
    logging.info("Browser initialized")
    return driver


def send_request_and_get_response(driver, message):
    logging.debug("Send request to chatbot interface")
    driver.implicitly_wait(10)
    textareas = driver.find_elements(By.CLASS_NAME, "textarea")
    print(len(textareas))
    textarea = textareas[-1]
    transfer_prompt(message, textarea)
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)))
    submit_button = driver.find_element(By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
    logging.debug("Push submit button")
    submit_button.click()

    # Wait a little time to avoid early fail.
    time.sleep(1)

    # Wait for stop button to be hidden. It means answer is finished.
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, MICROPHONE_CSS_SELECTOR)))

    message_bubbles = driver.find_elements(By.XPATH, ANSWER_XPATH)
    if not message_bubbles:
        logging.warning("No message found.")
        return ""
    last_message_bubble = message_bubbles[-1]
    html = last_message_bubble.get_attribute("outerHTML")
    clean_message = clean_chat_answer(html)
    logging.debug(f"Clean message ends with: {clean_message[-100:]}")
    return clean_message


def clean_chat_answer(html: str) -> str:
    """
    Find all DIVs containing code and remove unecessary decorations."
    """
    logging.debug("Clean chat answer")
    soup = BeautifulSoup(html, "html.parser")
    no_prose_divs = soup.find_all("div", class_="code-block")
    for div in no_prose_divs:
        if isinstance(div, Tag):
            code_tags = div.find_all("div", class_="formatted-code-block-internal-container")
            div.clear()
            for code in code_tags:
                div.append(code.get_text())
                div.insert_before("\n```\n")
                div.insert_after("\n```\n")
        else:
            code_tags = []

    clean_answer = soup.get_text(separator="\n").strip()
    while "\n\n" in clean_answer:
        clean_answer = clean_answer.replace("\n\n", "\n")
    return clean_answer


def main():
    driver = initialize_driver(Config())
    try:
        while True:
            user_request = input("Ask something (or 'quit'): ")
            if user_request.lower() == "quit":
                break
            response = send_request_and_get_response(driver, user_request)
            print("Answer:", response)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
