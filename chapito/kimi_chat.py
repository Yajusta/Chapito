import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt

URL: str = "https://www.kimi.com/chat/"
TIMEOUT_SECONDS: int = 120
QUESTION_XPATH: str = "//div[@class='chat-input-editor']"
SUBMIT_CSS_SELECTOR: str = ".send-button-container"
SUBMIT_DISABLE_CSS_SELECTOR: str = "div.send-button-container.disabled:not(.stop)"
ANSWER_XPATH: str = "//div[@class='markdown-container']"


def check_if_chat_loaded(driver) -> bool:
    driver.implicitly_wait(5)
    try:
        element = driver.find_element(By.XPATH, QUESTION_XPATH)
    except Exception as e:
        logging.warning("Can't find specific element in chat interface. Maybe it's not loaded yet.")
        return False
    return element is not None


def initialize_driver(config: Config):
    logging.info("Initializing browser for Kimi...")
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
    textarea = driver.find_element(By.XPATH, QUESTION_XPATH)
    transfer_prompt(message, textarea)
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)))
    time.sleep(1)
    submit_buttons = driver.find_elements(By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
    submit_button = submit_buttons[-1]
    logging.debug("Push submit button")
    submit_button.click()

    # Wait a little time to avoid early fail.
    time.sleep(3)

    # Wait for submit button to be available. It means answer is finished.
    wait = WebDriverWait(driver, TIMEOUT_SECONDS)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_DISABLE_CSS_SELECTOR)))

    time.sleep(1)
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

    no_prose_divs = soup.find_all("div", class_="segment-code")
    for div in no_prose_divs:
        if isinstance(div, Tag):
            code_tags = div.find_all("div", class_="segment-code-content")
            div.clear()
            for code in code_tags:
                div.append(code)
                code.insert_before("\n```\n")
                code.insert_after("\n```\n")
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
