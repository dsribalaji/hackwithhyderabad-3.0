"""Configuration — everything via environment variables (see .env.example)."""

import os


def get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


# Agent's own LLM (OpenAI-compatible)
LLM_BASE_URL = get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_API_KEY = get("LLM_API_KEY", "")
LLM_MODEL = get("LLM_MODEL", "qwen/qwen3-32b")

# Hindsight memory layer
HINDSIGHT_MODE = get("HINDSIGHT_MODE", "embedded")  # embedded | server
HINDSIGHT_URL = get("HINDSIGHT_URL", "http://localhost:8888")
HINDSIGHT_LLM_PROVIDER = get("HINDSIGHT_LLM_PROVIDER", "llamacpp")
HINDSIGHT_LLM_MODEL = get("HINDSIGHT_LLM_MODEL", "")
HINDSIGHT_LLM_API_KEY = get("HINDSIGHT_LLM_API_KEY", "")

BANK_ID = get("BANK_ID", "shopmind-demo")
