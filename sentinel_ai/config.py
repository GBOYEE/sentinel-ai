import os
from dotenv import load_dotenv

load_dotenv()

# GitHub App credentials
GH_APP_ID = os.getenv("GH_APP_ID", "0")
GH_APP_PRIVATE_KEY = os.getenv("GH_APP_PRIVATE_KEY", "")
GH_WEBHOOK_SECRET = os.getenv("GH_WEBHOOK_SECRET", "")
GH_REPO_MAP = os.getenv("GH_REPO_MAP", "")

# LLM settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Database & cache
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentinel.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Chroma memory
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")

# Sentinel settings
SCAN_TIMEOUT = int(os.getenv("SCAN_TIMEOUT", "300"))
ENABLE_STATIC_ANALYSIS = os.getenv("ENABLE_STATIC_ANALYSIS", "true").lower() == "true"
ENABLE_LLM_REVIEW = os.getenv("ENABLE_LLM_REVIEW", "true").lower() == "true"
