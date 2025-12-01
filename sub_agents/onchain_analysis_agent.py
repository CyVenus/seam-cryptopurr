import requests
from typing import Any, Dict, List, Optional

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.tools import google_search

from ..config import DEFAULT_MODEL


# helper function to fetch dexscreener pairs
def fetch_dexscreener_pairs(
        query: str,
        limit: int = 1,
        tool_context: Optional[ToolContext] = None,
    ) -> Dict[str, Any]:

    """
    Calls Dexscreener api endpoint with a query.
    Example queries:
      - token name (e.g. "SACHI")
      - token address / mint
      - pair URL or pair address

    Returns a compact JSON with at most `limit` pairs and only useful fields.
    """

    if not query:
        raise ValueError("query is required for Dexscreener search.")

    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    pairs: List[Dict[str, Any]] = data.get("pairs") or []
    pairs = pairs[:limit] if limit > 0 else pairs
    compact_pairs: List[Dict[str, Any]] = []

    for p in pairs:
        # Extract needy fields to save tokens
        compact_pairs.append(
            {
                "chainId": p.get("chainId"),
                "dexId": p.get("dexId"),
                "url": p.get("url"),
                "pairAddress": p.get("pairAddress"),
                "baseToken": {
                    "address": p.get("baseToken", {}).get("address"),
                    "name": p.get("baseToken", {}).get("name"),
                    "symbol": p.get("baseToken", {}).get("symbol"),
                },
                "quoteToken": {
                    "address": p.get("quoteToken", {}).get("address"),
                    "name": p.get("quoteToken", {}).get("name"),
                    "symbol": p.get("quoteToken", {}).get("symbol"),
                },
                "priceNative": p.get("priceNative"),
                "priceUsd": p.get("priceUsd"),
                "txns": p.get("txns", {}),
                "volume": p.get("volume", {}),
                "priceChange": p.get("priceChange", {}),
                "liquidity": p.get("liquidity", {}),
                "fdv": p.get("fdv"),
                "marketCap": p.get("marketCap"),
                "pairCreatedAt": p.get("pairCreatedAt"),
                "info": {
                    "imageUrl": p.get("info", {}).get("imageUrl"),
                    "websites": p.get("info", {}).get("websites", []),
                    "socials": p.get("info", {}).get("socials", []),
                },
                "labels": p.get("labels", []),
                "boosts": p.get("boosts", {}),
            }
        )

    return {
        "query": query,
        "count": len(compact_pairs),
        "pairs": compact_pairs,
    }


dexscreener_tool = FunctionTool(
    func=fetch_dexscreener_pairs,
)


ONCHAIN_FETCH_INSTRUCTION = """
You are the ON-CHAIN FETCH AGENT.

Your job:
1) Understand which token/pair the user wants analyzed.
   - The user might give:
       * token name (e.g. 'Sachicoin')
       * symbol (e.g. 'SACHI')
       * contract/mint address
       * Dexscreener URL
2) Build a good search string for Dexscreener and call:
       fetch_dexscreener_pairs(query=<string>, limit=1)
       use tool_context to pass in the query
       the query is the token which the user wants to analyze 
       (its the token name so pass the token name from the user message)
3) Take the tool output and store it under the state key 'onchain_raw_data'.

Guidelines:
- If the user supplies an explicit mint/contract or Dexscreener URL, prefer
  using that as the query.
- If only a name/symbol is given, use that as query and rely on Dexscreener
  to resolve the most relevant pair.
- Do NOT generate any user-facing explanation here.
- Keep all information exactly as returned by the tool; do not reformat heavily.
"""

onchain_fetch_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="onchain_fetch_agent",
    instruction=ONCHAIN_FETCH_INSTRUCTION,
    description=(
        "Fetches on-chain market data for a token/pair using Dexscreener and "
        "stores it as 'onchain_raw_data' in state."
    ),
    tools=[dexscreener_tool],
    output_key="onchain_raw_data",
)



ONCHAIN_SUMMARY_INSTRUCTION = """
You are the ON-CHAIN RISK SUMMARY AGENT.

Read 'onchain_raw_data' from state (Dexscreener pair data). Focus on the first pair.

**Data Structure:**
- `baseToken`: name, symbol, address
- `priceUsd`, `liquidity.usd`, `volume.h24`, `fdv`, `marketCap`
- `txns.h24`: buys/sells counts
- `priceChange.h24`: price movement
- `pairCreatedAt`: token age
- `labels`, `info.websites`, `info.socials`

**Optional Google Search:**
If available, search for: `"'token_name' 'symbol' scam"` to check for public warnings. If tools unavailable, note it.

**Output Format:**
1. **Basic Info**: Name, symbol, chain, price, Dexscreener URL
2. **Metrics**: Liquidity USD, 24h volume, buys/sells ratio, price change
3. **Risk Assessment**: Token age, liquidity depth, volume health, any labels
4. **External Signals**: Scam reports found (if searched) or note if not searched
5. **Overall Rating**: "Very high risk" / "High risk" / "Moderate risk" / "Cautious" / "No obvious red flags but still risky" + 3-6 bullet points explaining why

**Rules:**
- NO investment advice (no buy/sell/hold recommendations)
- Can state risk levels: "extremely high risk due to XYZ" or "no major warnings but low liquidity makes it speculative"
- Keep it beginner-friendly
"""

onchain_summary_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="onchain_summary_agent",
    instruction=ONCHAIN_SUMMARY_INSTRUCTION,
    description=(
        "Reads 'onchain_raw_data' from Dexscreener and optionally uses Google "
        "Search to check for scam/rug warnings, then produces a clear risk summary."
    ),
    tools=[google_search],
)


onchain_analysis_agent = SequentialAgent(
    name="onchain_analysis_agent",
    description=(
        "Sequential pipeline that fetches on-chain token data from DexScreener, "
        "then analyzes and summarizes the results into a user-friendly risk assessment "
        "with liquidity metrics, volume analysis, and optional scam detection."
    ),
    sub_agents=[
        onchain_fetch_agent,
        onchain_summary_agent,
    ],
)
