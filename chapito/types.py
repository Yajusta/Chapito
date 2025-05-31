from enum import Enum


class OsType(Enum):
    UNKNOWN = 0
    WINDOWS = 1
    LINUX = 2
    MACOS = 3


class Chatbot(Enum):
    AI_STUDIO = "ai_studio"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    DUCKDUCKGO = "duckduckgo"
    GEMINI = "gemini"
    GITHUB = "github"
    GROK = "grok"
    KIMI = "kimi"
    MISTRAL = "mistral"
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    QWEN = "qwen"
