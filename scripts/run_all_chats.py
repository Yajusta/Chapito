import asyncio
import logging
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
from chapito.types import Chatbot

# The user is asking me to create a github action that runs a test message each provdir and returns the response

async def run_test_for_chatbot(chatbot_module, chatbot_name):
    """Initializes a chatbot, sends a message, and prints the response."""
    print(f"--- Testing {chatbot_name} ---")
    browser = None
    try:
        config = Config()
        browser, tab = await chatbot_module.initialize_tab(config)
        response = await chatbot_module.send_request_and_get_response(
            tab, "Hello! What is the capital of France?"
        )
        print(f"Response from {chatbot_name}: {response}")
    except Exception as e:
        print(f"Error testing {chatbot_name}: {e}")
    finally:
        if browser:
            await browser.stop()
    print(f"--- Finished testing {chatbot_name} ---\n")


async def main():
    """Runs the test for all available chatbots."""
    chatbots = {
        "AI Studio": ai_studio_chat,
        "Anthropic": anthropic_chat,
        "DeepSeek": deepseek_chat,
        "DuckDuckGo": duckduckgo_chat,
        "Gemini": gemini_chat,
        "Grok": grok_chat,
        "Kimi": kimi_chat,
        "Mistral": mistral_chat,
        "OpenAI": openai_chat,
        "Perplexity": perplexity_chat,
        "Qwen": qwen_chat,
    }

    for name, module in chatbots.items():
        await run_test_for_chatbot(module, name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
