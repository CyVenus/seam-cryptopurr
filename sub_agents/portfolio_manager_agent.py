import time
import sqlite3
from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, ToolContext

from ..config import PORTFOLIO_DB_PATH, DEFAULT_MODEL
from .helper_func_tools.general_helper_tools import (
    evm_scan_address,
    btc_scan_address,
    sol_scan_address,
)

DB_PATH = PORTFOLIO_DB_PATH

# setup database for portfolio
def _init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio (
            address TEXT NOT NULL,
            chain TEXT NOT NULL,
            family TEXT NOT NULL,
            native_balance TEXT,
            native_unit TEXT,
            last_updated INTEGER,
            PRIMARY KEY (address, chain)
        )
        """
    )
    conn.commit()
    conn.close()


_init_db()


def add_address_to_portfolio(
        address: str,
        chain_hint: Optional[str] = None,
        tool_context: Optional[ToolContext] = None,
    ) -> Dict[str, Any]:
    """
    Add a wallet address to the portfolio DB.

    Steps:
    1) Decide family: btc / evm / solana.
    2) Call the appropriate scanner function from general_helper_tools:
         - evm_scan_address
         - btc_scan_address
         - sol_scan_address
    3) Store result in SQLite.
    4) Return a compact JSON including what was stored.

    """
    if not address:
        raise ValueError("address is required")

    family: str
    chain: str

    if chain_hint:
        if chain_hint.lower() in {"btc", "bitcoin"}:
            family, chain = "btc", "btc"
        elif chain_hint.lower() in {"sol", "solana"}:
            family, chain = "solana", "solana"
        else:
            family, chain = "evm", chain_hint.lower()
    else:
        if address.startswith("0x") and len(address) == 42:
            family, chain = "evm", "ethereum"
        elif address.startswith(("bc1", "1", "3")):
            family, chain = "btc", "btc"
        else:
            family, chain = "solana", "solana"

    # helper function to scan blockchain
    if family == "evm":
        snapshot = evm_scan_address(address=address, chain=chain, limit=20)
    elif family == "btc":
        snapshot = btc_scan_address(address=address, limit=20)
    else:
        snapshot = sol_scan_address(address=address, limit=20)

    native_balance = snapshot.get("native_balance")
    native_unit = snapshot.get("native_unit")
    ts = int(time.time())

    # store in database
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO portfolio
            (address, chain, family, native_balance, native_unit, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (address, chain, family, native_balance, native_unit, ts),
    )
    conn.commit()
    conn.close()

    return {
        "stored": True,
        "address": address,
        "family": family,
        "chain": chain,
        "native_balance": native_balance,
        "native_unit": native_unit,
        "last_updated": ts,
        "snapshot": snapshot,
    }


add_to_portfolio_tool = FunctionTool(
    func=add_address_to_portfolio,
)


def refresh_and_aggregate_portfolio(
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Refresh all portfolio entries by re-scanning blockchains
    and compute totals per chain using ONLY Python.

    Returns:
    {
      "total_addresses": N,
      "by_chain": [
        {
          "family": "evm" | "btc" | "solana",
          "chain": "ethereum" | "btc" | "solana" | ...,
          "addresses": [
            {
              "address": "...",
              "native_balance": "<string>",
              "native_unit": "wei" | "sats" | "lamports",
            }, ...
          ],
          "total_native": "<string>",
          "native_unit": "...",
        },
        ...
      ]
    }
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT address, chain, family FROM portfolio"
    )
    rows = cur.fetchall()
    conn.close()

    by_chain: Dict[str, Dict[str, Any]] = {}
    total_addresses = 0

    for address, chain, family in rows:
        total_addresses += 1

        # Re-scan using helper functions (fresh data)
        if family == "evm":
            snap = evm_scan_address(address=address, chain=chain, limit=10)
        elif family == "btc":
            snap = btc_scan_address(address=address, limit=10)
        else:
            snap = sol_scan_address(address=address, limit=10)

        bal_str = snap.get("native_balance") or "0"
        unit = snap.get("native_unit") or "unknown"

        # Convert balance string to int safely for summing
        try:
            bal_int = int(bal_str)
        except (TypeError, ValueError):
            bal_int = 0

        key = f"{family}:{chain}"
        if key not in by_chain:
            by_chain[key] = {
                "family": family,
                "chain": chain,
                "addresses": [],
                "total_native_int": 0,
                "native_unit": unit,
            }

        by_chain[key]["addresses"].append(
            {
                "address": address,
                "native_balance": bal_str,
                "native_unit": unit,
            }
        )
        by_chain[key]["total_native_int"] += bal_int

    # Convert totals back to string
    result_by_chain = []
    for key, entry in by_chain.items():
        entry_out = {
            "family": entry["family"],
            "chain": entry["chain"],
            "addresses": entry["addresses"],
            "total_native": str(entry["total_native_int"]),
            "native_unit": entry["native_unit"],
        }
        result_by_chain.append(entry_out)

    return {
        "total_addresses": total_addresses,
        "by_chain": result_by_chain,
    }


refresh_portfolio_tool = FunctionTool(
    func=refresh_and_aggregate_portfolio,
)


PORTFOLIO_MANAGER_INSTRUCTION = """
You are the PORTFOLIO MANAGER AGENT.
You ONLY handle portfolio-related tasks, NOT raw transaction checks.

1) Add wallet to portfolio
   - User says things like:
       "this is my address",
       "save this wallet",
       "add this to my portfolio",
       "remember these addresses".
   - For each address, call:
       add_address_to_portfolio(address, chain_hint?)
   - Then explain in simple terms what you did:
       chain, current balance, and confirmation that it's stored.

2) Show portfolio / total holdings
   - User says things like:
       "show my portfolio",
       "total portfolio",
       "what do I have?",
       "balances for all my wallets".
   - Call:
       refresh_and_aggregate_portfolio()
   - Then summarize:
       * how many addresses in total,
       * group by chain/family,
       * per-chain total native balance,
       * list addresses with their balances.
   - Keep it readable, not raw JSON.

Rules:
- Never add an address unless the user clearly indicates it is theirs
  or they explicitly ask you to store/save/remember it.
- Do NOT do blockchain math yourself; trust the numbers from the tools.
"""

portfolio_manager_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="portfolio_manager_agent",
    instruction=PORTFOLIO_MANAGER_INSTRUCTION,
    description=(
        "Adds user wallets to a portfolio DB and shows aggregated holdings "
        "using shared blockchain helper tools."
    ),
    tools=[add_to_portfolio_tool, refresh_portfolio_tool],
)
