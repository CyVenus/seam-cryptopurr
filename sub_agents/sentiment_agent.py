import requests
from typing import Any, Dict, Optional

from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents import LlmAgent

from ..config import DEFAULT_MODEL


def fetch_fear_greed_index(
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Fetches the latest Crypto Fear & Greed Index from alternative.me.
    Returns JSON like:
    {
        "value": "63",
        "classification": "Greed",
        "timestamp": "1712345678"
    }
    """
    url = "https://api.alternative.me/fng/?limit=1&format=json"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    if not data.get("data") or len(data["data"]) == 0:
        raise ValueError("No sentiment index data received.")

    entry = data["data"][0]

    return {
        "value": entry.get("value", ""),
        "classification": entry.get("value_classification", ""),
        "timestamp": entry.get("timestamp", ""),
    }


fear_greed_tool = FunctionTool(
    func=fetch_fear_greed_index,
)

SENTIMENT_INSTRUCTION = """
You are the CRYPTO SENTIMENT AGENT.

Your job:
1) ALWAYS call the Python tool 'fetch_fear_greed_index' to retrieve the
   latest sentiment index (Fear & Greed Index).
2) Take the returned JSON and create a clean human-readable summary.

Formatting:
- Bold the classification (Fear, Extreme Fear, Neutral, Greed, Extreme Greed)
- Show the numeric index (0–100)
- Briefly explain what this sentiment usually means, but:
  * NO financial advice
  * NO telling user what to buy/sell

Example Output:
"**Greed (63)** — The market is leaning optimistic. Higher values indicate
stronger positive sentiment, while lower values indicate fear. This index is
a short-term sentiment indicator, not investment guidance."

Do NOT call multiple tools.
Do NOT generate data yourself.
Always trust and use the tool output.
"""

sentiment_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="sentiment_agent",
    instruction=SENTIMENT_INSTRUCTION,
    description="Fetches and summarizes crypto market sentiment using Fear & Greed Index.",
    tools=[fear_greed_tool],
)
