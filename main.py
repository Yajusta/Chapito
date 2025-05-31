from chapito.config import Config
from chapito import (
    ai_studio_chat,
    anthropic_chat,
    deepseek_chat,
    duckduckgo_chat,
    gemini_chat,
    grok_chat,
    kimi_chat,
    mistral_chat,
    openai_chat,
    perplexity_chat,
    qwen_chat,
)
from chapito.proxy import init_proxy
from chapito.tools.tools import check_official_version, greeting
from chapito.types import Chatbot

__version__ = "0.1.12"


def main():
    greeting(__version__)
    config = Config()
    check_official_version(__version__)

    if config.chatbot == Chatbot.AI_STUDIO:
        driver = ai_studio_chat.initialize_driver(config)
        init_proxy(driver, deepseek_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.ANTHROPIC:
        driver = anthropic_chat.initialize_driver(config)
        init_proxy(driver, anthropic_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.DEEPSEEK:
        driver = deepseek_chat.initialize_driver(config)
        init_proxy(driver, deepseek_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.DUCKDUCKGO:
        driver = duckduckgo_chat.initialize_driver(config)
        init_proxy(driver, duckduckgo_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.GEMINI:
        driver = gemini_chat.initialize_driver(config)
        init_proxy(driver, gemini_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.GROK:
        driver = grok_chat.initialize_driver(config)
        init_proxy(driver, grok_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.KIMI:
        driver = kimi_chat.initialize_driver(config)
        init_proxy(driver, kimi_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.MISTRAL:
        driver = mistral_chat.initialize_driver(config)
        init_proxy(driver, mistral_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.OPENAI:
        driver = openai_chat.initialize_driver(config)
        init_proxy(driver, openai_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.PERPLEXITY:
        driver = perplexity_chat.initialize_driver(config)
        init_proxy(driver, perplexity_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.QWEN:
        driver = qwen_chat.initialize_driver(config)
        init_proxy(driver, qwen_chat.send_request_and_get_response, config)


if __name__ == "__main__":
    main()
