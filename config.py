import os
from google.genai import types as genai_types


# The 2.5 models currently reject tool/function calls, so fall back to
# Gemini 1.5 variants which fully support the ADK tool infrastructure.
DEFAULT_MODEL = "gemini-2.5-flash"
FAST_MODEL = "gemini-2.5-flash"
ADVANCED_MODEL = "gemini-2.5-pro"


# Environment variables
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# SMTP configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# Database paths (hardcoded, will be in git)
PORTFOLIO_DB_PATH = "portfolio.db"
ALERTS_DB_PATH = "alerts.db"

# API endpoints
COINGECKO_MCP_URL = os.getenv("COINGECKO_MCP_URL", "https://mcp.api.coingecko.com/mcp")
