from typing import Any, Dict, List, Optional

import requests
from google.adk.tools import FunctionTool, ToolContext

from ...config import ETHERSCAN_API_KEY



# Map human chain names -> chainId for Etherscan v2 API
CHAIN_IDS: Dict[str, int] = {
    "ethereum": 1,
    "polygon": 137,
    "bsc": 56,
    "arbitrum": 42161,
    "optimism": 10,
    "base": 8453,
    "avalanche": 43114,
    # you can keep adding more here
}


def evm_scan_address(
    address: str,
    chain: str = "ethereum",
    limit: int = 20,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Scan an EVM address using the Etherscan v2 multi-chain API.

    - address: 0x-prefixed address (42 chars)
    - chain: key in CHAIN_IDS; defaults to 'ethereum'
    - limit: max number of recent normal transactions to include

    Returns a compact snapshot:
    {
      "family": "evm",
      "chain": "ethereum",
      "chainId": 1,
      "address": "...",
      "native_balance": "<wei>",
      "native_unit": "wei",
      "tx_count": N,
      "latest_timestamp": 1234567890,
      "transactions": [
        {
          "hash": "...",
          "from": "...",
          "to": "...",
          "value": "<wei>",
          "timestamp": 1234567890,
          "status": "success" | "failed",
        },
        ...
      ],
    }
    """
    if not ETHERSCAN_API_KEY:
        raise RuntimeError("Missing ETHERSCAN_API_KEY")

    if not address.startswith("0x") or len(address) != 42:
        raise ValueError("Invalid EVM address; expected 0x + 40 hex chars.")

    chain_id = CHAIN_IDS.get(chain, 1)

    base_url = "https://api.etherscan.io/v2/api"

    tx_params = {
        "chainid": chain_id,
        "module": "account",
        "action": "txlist",
        "address": address,
        "page": 1,
        "offset": limit,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY,
    }
    tx_resp = requests.get(base_url, params=tx_params, timeout=12)
    tx_resp.raise_for_status()
    tx_data = tx_resp.json() or {}
    txs_raw: List[Dict[str, Any]] = tx_data.get("result") or []

    txs: List[Dict[str, Any]] = []
    latest_ts: Optional[int] = None

    for tx in txs_raw[:limit]:
        ts = int(tx.get("timeStamp", 0)) if tx.get("timeStamp") else None
        if ts is not None and (latest_ts is None or ts > latest_ts):
            latest_ts = ts

        txs.append(
            {
                "hash": tx.get("hash"),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": tx.get("value"),
                "timestamp": ts,
                "status": "failed" if tx.get("isError") == "1" else "success",
            }
        )
    bal_params = {
        "chainid": chain_id,
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": ETHERSCAN_API_KEY,
    }
    bal_resp = requests.get(base_url, params=bal_params, timeout=12)
    bal_resp.raise_for_status()
    bal_data = bal_resp.json() or {}
    native_balance = bal_data.get("result")

    return {
        "family": "evm",
        "chain": chain,
        "chainId": chain_id,
        "address": address,
        "native_balance": native_balance,
        "native_unit": "wei",
        "tx_count": len(txs),
        "latest_timestamp": latest_ts,
        "transactions": txs,
    }


evm_scan_tool = FunctionTool(
    func=evm_scan_address,
)


def btc_scan_address(
    address: str,
    limit: int = 20,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Scan a Bitcoin address using Blockstream's public API.

    Uses:
      - /address/{address}    -> balance info
      - /address/{address}/txs -> recent transactions

    Returns:
    {
      "family": "btc",
      "chain": "btc",
      "address": "...",
      "native_balance": "<sats>",
      "native_unit": "sats",
      "tx_count": N,
      "latest_timestamp": 1234567890,
      "transactions": [
        {
          "hash": "...",
          "timestamp": 1234567890,
          "status": "confirmed" | "unconfirmed",
        },
        ...
      ],
    }
    """
    if not address or len(address) < 20:
        raise ValueError("Invalid BTC address.")

    addr_url = f"https://blockstream.info/api/address/{address}"
    addr_resp = requests.get(addr_url, timeout=12)
    addr_resp.raise_for_status()
    addr_data = addr_resp.json() or {}

    chain_stats = addr_data.get("chain_stats") or {}
    funded = chain_stats.get("funded_txo_sum") or 0
    spent = chain_stats.get("spent_txo_sum") or 0
    native_balance = str(int(funded) - int(spent))

    tx_url = f"https://blockstream.info/api/address/{address}/txs"
    tx_resp = requests.get(tx_url, timeout=12)
    tx_resp.raise_for_status()
    txs_raw: List[Dict[str, Any]] = tx_resp.json() or []

    txs: List[Dict[str, Any]] = []
    latest_ts: Optional[int] = None

    for tx in txs_raw[:limit]:
        status = tx.get("status") or {}
        ts = status.get("block_time")
        if ts is not None and (latest_ts is None or ts > latest_ts):
            latest_ts = ts

        txs.append(
            {
                "hash": tx.get("txid"),
                "timestamp": ts,
                "status": "confirmed" if status.get("confirmed") else "unconfirmed",
            }
        )

    return {
        "family": "btc",
        "chain": "btc",
        "address": address,
        "native_balance": native_balance,
        "native_unit": "sats",
        "tx_count": len(txs),
        "latest_timestamp": latest_ts,
        "transactions": txs,
    }


btc_scan_tool = FunctionTool(
    func=btc_scan_address,
)


def sol_scan_address(
    address: str,
    limit: int = 20,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Scan a Solana address using Solscan.

    Uses:
      - /account/{address}             -> lamport balance
      - /account/transactions?address= -> recent txs

    Returns:
    {
      "family": "solana",
      "chain": "solana",
      "address": "...",
      "native_balance": "<lamports>",
      "native_unit": "lamports",
      "tx_count": N,
      "latest_timestamp": 1234567890,
      "transactions": [
        {
          "hash": "...",
          "timestamp": 1234567890,
          "status": "...",
        },
        ...
      ],
    }
    """
    if not address or len(address) < 30:
        raise ValueError("Invalid Solana address.")

    headers = {
        "accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    acc_url = f"https://public-api.solscan.io/account/{address}"
    acc_resp = requests.get(acc_url, headers=headers, timeout=12)
    acc_resp.raise_for_status()
    acc_data = acc_resp.json() or {}
    native_balance = str(acc_data.get("lamports") or 0)

    tx_url = "https://public-api.solscan.io/account/transactions"
    tx_params = {"address": address, "limit": limit}
    tx_resp = requests.get(tx_url, headers=headers, params=tx_params, timeout=12)
    tx_resp.raise_for_status()
    txs_raw: List[Dict[str, Any]] = tx_resp.json() or []

    txs: List[Dict[str, Any]] = []
    latest_ts: Optional[int] = None

    for tx in txs_raw[:limit]:
        sig = tx.get("tx_hash") or tx.get("signature")
        ts = tx.get("block_time")
        if ts is not None and (latest_ts is None or ts > latest_ts):
            latest_ts = ts

        txs.append(
            {
                "hash": sig,
                "timestamp": ts,
                "status": tx.get("status"),
            }
        )

    return {
        "family": "solana",
        "chain": "solana",
        "address": address,
        "native_balance": native_balance,
        "native_unit": "lamports",
        "tx_count": len(txs),
        "latest_timestamp": latest_ts,
        "transactions": txs,
    }


sol_scan_tool = FunctionTool(
    func=sol_scan_address,
)
