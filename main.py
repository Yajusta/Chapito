import asyncio
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


async def main():
    greeting(__version__)
    config = Config()
    check_official_version(__version__)

    if config.chatbot == Chatbot.AI_STUDIO:
        browser, tab = await ai_studio_chat.initialize_tab(config)
        init_proxy(browser, tab, ai_studio_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.ANTHROPIC:
        browser, tab = await anthropic_chat.initialize_tab(config)
        init_proxy(browser, tab, anthropic_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.DEEPSEEK:
        browser, tab = await deepseek_chat.initialize_tab(config)
        init_proxy(browser, tab, deepseek_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.DUCKDUCKGO:
        browser, tab = await duckduckgo_chat.initialize_tab(config)
        init_proxy(browser, tab, duckduckgo_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.GEMINI:
        browser, tab = await gemini_chat.initialize_tab(config)
        init_proxy(browser, tab, gemini_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.GROK:
        browser, tab = await grok_chat.initialize_tab(config)
        init_proxy(browser, tab, grok_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.KIMI:
        browser, tab = await kimi_chat.initialize_tab(config)
        init_proxy(browser, tab, kimi_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.MISTRAL:
        browser, tab = await mistral_chat.initialize_tab(config)
        init_proxy(browser, tab, mistral_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.OPENAI:
        browser, tab = await openai_chat.initialize_tab(config)
        init_proxy(browser, tab, openai_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.PERPLEXITY:
        browser, tab = await perplexity_chat.initialize_tab(config)
        init_proxy(browser, tab, perplexity_chat.send_request_and_get_response, config)

    if config.chatbot == Chatbot.QWEN:
        browser, tab = await qwen_chat.initialize_tab(config)
        init_proxy(browser, tab, qwen_chat.send_request_and_get_response, config)


if __name__ == "__main__":
    asyncio.run(main())
