import html
import re
import requests
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.tools import google_search

from ..config import DEFAULT_MODEL

def _fetch_rss(
    url: str,
    source_name: str,
    category: str,
    limit: int = 5,
) -> Dict[str, Any]:
    """
    Generic RSS fetcher for crypto news sources.

    Fetches and parses RSS XML feeds, extracting article metadata including
    title, link, and publication date. Returns a structured dictionary with
    source information and article items.

    Args:
        url: RSS feed URL to fetch
        source_name: Name identifier for the news source (e.g., "coindesk", "decrypt")
        category: News category classification (e.g., "headlines", "altcoins", "topic")
        limit: Maximum number of articles to return (default: 5)

    Returns:
        Dict containing:
            - source: Source name identifier
            - category: News category
            - items: List of article dictionaries with keys:
                * title: Article title (HTML unescaped)
                * link: Article URL
                * published: Publication date string

    Raises:
        requests.HTTPError: If the RSS feed request fails
        xml.etree.ElementTree.ParseError: If RSS XML parsing fails

    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    content = resp.text

    root = ET.fromstring(content)
    items: List[Dict[str, Any]] = []

    for item in root.findall(".//item"):
        title_node = item.find("title")
        link_node = item.find("link")
        date_node = item.find("pubDate")

        title = html.unescape(title_node.text) if title_node is not None and title_node.text else ""
        link = link_node.text.strip() if link_node is not None and link_node.text else ""
        pub_date = date_node.text.strip() if date_node is not None and date_node.text else ""

        if not title or not link:
            continue

        title = re.sub(r"\s+", " ", title).strip()

        items.append(
            {
                "title": title,
                "link": link,
                "published": pub_date,
            }
        )

        if len(items) >= limit:
            break

    return {
        "source": source_name,
        "category": category,
        "items": items,
    }

def fetch_coindesk_decrypt_headlines(
      limit_per_source: int = 5,
      tool_context: Optional[ToolContext] = None,
  ) -> Dict[str, Any]:
    """
    Fetch top general cryptocurrency headlines from CoinDesk and Decrypt RSS feeds.

    Aggregates news from two major crypto news sources, returning a structured
    bundle of recent headlines suitable for market overview and general crypto updates.

    Args:
        limit_per_source: Maximum number of articles to fetch from each source (default: 5)

    Returns:
        Dict containing:
            - category: "headlines"
            - sources: List of source dictionaries, each containing:
                * source: Source identifier ("coindesk" or "decrypt")
                * category: "headlines"
                * items: List of article dictionaries with title, link, published

    Raises:
        requests.HTTPError: If RSS feed requests fail
        xml.etree.ElementTree.ParseError: If RSS XML parsing fails
    """

    coindesk_url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    coindesk = _fetch_rss(
        url=coindesk_url,
        source_name="coindesk",
        category="headlines",
        limit=limit_per_source,
    )


    decrypt_url = "https://decrypt.co/feed"
    decrypt = _fetch_rss(
        url=decrypt_url,
        source_name="decrypt",
        category="headlines",
        limit=limit_per_source,
    )

    return {
        "category": "headlines",
        "sources": [coindesk, decrypt],
    }


def fetch_cointelegraph_altcoin_headlines(
      limit: int = 5,
      tool_context: Optional[ToolContext] = None,
  ) -> Dict[str, Any]:
    """
    Fetch top altcoin-focused cryptocurrency news from CoinTelegraph RSS feed.

    Retrieves news articles focused on altcoins, DeFi, memecoins, and emerging
    blockchain projects. Ideal for users interested in alternative cryptocurrencies
    beyond Bitcoin and Ethereum.

    Args:
        limit: Maximum number of articles to return (default: 5)

    Returns:
        Dict containing:
            - category: "altcoins"
            - sources: List with single source dictionary containing:
                * source: "cointelegraph"
                * category: "altcoins"
                * items: List of article dictionaries with title, link, published

    Raises:
        requests.HTTPError: If RSS feed request fails
        xml.etree.ElementTree.ParseError: If RSS XML parsing fails
    """
    cointelegraph_url = "https://cointelegraph.com/rss"
    ct = _fetch_rss(
        url=cointelegraph_url,
        source_name="cointelegraph",
        category="altcoins",
        limit=limit,
    )

    return {
        "category": "altcoins",
        "sources": [ct],
    }

# Wrap tools
coindesk_decrypt_tool = FunctionTool(
    func=fetch_coindesk_decrypt_headlines,
)

cointelegraph_tool = FunctionTool(
    func=fetch_cointelegraph_altcoin_headlines,
)


HEADLINES_FETCH_INSTRUCTION = """
You are the HEADLINES FETCH AGENT.

Your job:
- Use the coindesk_decrypt_tool with limit_per_source=5 to get general crypto headlines.
- Store the result in state under 'headlines_data'.
- Do NOT summarize. Just fetch and store.
"""

headlines_fetch_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="headlines_fetch_agent",
    instruction=HEADLINES_FETCH_INSTRUCTION,
    description="Fetches general crypto headlines from CoinDesk and Decrypt RSS feeds.",
    tools=[coindesk_decrypt_tool],
    output_key="headlines_data",
)

ALTCOINS_FETCH_INSTRUCTION = """
You are the ALTCOINS FETCH AGENT.

Your job:
- Use the cointelegraph_tool with limit=5 to get altcoin/DeFi news.
- Store the result in state under 'altcoins_data'.
- Do NOT summarize. Just fetch and store.
"""

altcoins_fetch_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="altcoins_fetch_agent",
    instruction=ALTCOINS_FETCH_INSTRUCTION,
    description="Fetches altcoin-focused news from CoinTelegraph RSS feed.",
    tools=[cointelegraph_tool],
    output_key="altcoins_data",
)

GOOGLE_NEWS_FETCH_INSTRUCTION = """
You are the GOOGLE NEWS FETCH AGENT.

Your job:
- Use google_search to find recent cryptocurrency news articles.
- Search for: "cryptocurrency news" or "crypto market news" (or similar broad terms).
- Store the search results in state under 'google_news_data'.
- Format as: { "category": "google_news", "items": [...] }
- Do NOT summarize. Just fetch and store.
"""

google_news_fetch_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="google_news_fetch_agent",
    instruction=GOOGLE_NEWS_FETCH_INSTRUCTION,
    description="Fetches general crypto news using Google Search.",
    tools=[google_search],
    output_key="google_news_data",
)

overall_news_parallel_agent = ParallelAgent(
    name="overall_news_parallel_agent",
    description="Runs three news fetch agents in parallel for comprehensive market coverage.",
    sub_agents=[
        headlines_fetch_agent,
        altcoins_fetch_agent,
        google_news_fetch_agent,
    ],
)


NEWS_SUMMARY_INSTRUCTION = """
You are the NEWS SUMMARY AGENT.

Context:
- Three data sources are available in state:
  - 'headlines_data': CoinDesk + Decrypt headlines
  - 'altcoins_data': CoinTelegraph altcoin news
  - 'google_news_data': Google Search results

Your job:
- Combine all three sources into a comprehensive news digest.
- Group by category: Headlines, Altcoins, General News
- Show 3-6 top stories per category.
- Deduplicate similar stories across sources.

Format:
- **Category: Headlines**
  - Story 1: [Title] - [Brief explanation] - Source: [source] - [link]
  - Story 2: ...
- **Category: Altcoins**
  - Story 1: ...
- **Category: General News**
  - Story 1: ...

Rules:
- Aim for 8-12 total stories across all categories.
- Keep explanations tight (1-2 sentences per item).
- NO trading advice.
"""

news_summary_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="news_summary_agent",
    instruction=NEWS_SUMMARY_INSTRUCTION,
    description=(
        "Combines results from parallel news fetch agents into a comprehensive "
        "formatted digest."
    ),
)

news_research_agent = SequentialAgent(
    name="news_research_agent",
    description=(
        "Fetches crypto news from multiple sources in parallel, then summarizes "
        "all results into a comprehensive digest."
    ),
    sub_agents=[
        overall_news_parallel_agent,
        news_summary_agent,
    ],
)

