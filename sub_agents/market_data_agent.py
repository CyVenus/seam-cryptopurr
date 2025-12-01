from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

from ..config import DEFAULT_MODEL, COINGECKO_MCP_URL

market_data_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="market_data_agent",
    description=(
        "Specialist agent for crypto market data using CoinGecko MCP. "
        "Answers questions about prices, OHLC, market cap, volume, and top movers."
    ),
    instruction=(
        "You are a crypto market data specialist.\n"
        "- ALWAYS use the CoinGecko MCP tools for anything involving prices, "
        "market cap, volume, OHLC, trending coins, or top gainers/losers.\n"
        "- Never guess numbers. If tools fail or rate-limit, explain clearly what went wrong.\n"
        "- When user provides a list of coins or portfolio, fetch data for each and then "
        "summarize clearly in human language.\n"
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=COINGECKO_MCP_URL,
            )
        )
    ],
)
