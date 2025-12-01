from google.adk.agents import LlmAgent, SequentialAgent

from ..config import DEFAULT_MODEL
from .helper_func_tools.general_helper_tools import (
    evm_scan_tool,
    btc_scan_tool,
    sol_scan_tool,
)


SCAN_INSTRUCTION = """
You are the BLOCKCHAIN SCAN AGENT.

Goal:
- Given a single public address from the user,
  detect which chain it belongs to (BTC / EVM / Solana),
  then call the correct FunctionTool.

Detection rules:
- If address starts with '0x' and length ~42  -> EVM.
- If address starts with 'bc1', '1', or '3'   -> BTC.
- Otherwise (base58-like, length ~32–44)      -> Solana.

What to do:
1. Extract the address from the user message.
2. Decide its family (btc / evm / solana).
3. Call exactly one of:
     - evm_scan_address(address, chain="ethereum", limit=20)  # unless user says another EVM chain
     - btc_scan_address(address, limit=20)
     - sol_scan_address(address, limit=20)
4. Store the tool's return JSON into state as 'blockchain_scan_snapshot'.
5. Do NOT explain the result; just perform the scan.
"""

blockchain_scan_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="blockchain_scan_agent",
    instruction=SCAN_INSTRUCTION,
    description="Detects chain from address and scans it with the correct helper tool.",
    tools=[evm_scan_tool, btc_scan_tool, sol_scan_tool],
    output_key="blockchain_scan_snapshot",
)



SUMMARY_INSTRUCTION = """
You are the BLOCKCHAIN TRANSACTION SUMMARY AGENT.

Context:
- 'blockchain_scan_snapshot' is already in state.
  It has fields like:
  {
    "family": "evm" | "btc" | "solana",
    "chain":  "ethereum" | "btc" | "solana" | ...,
    "address": "...",
    "native_balance": "<string>",
    "native_unit": "wei" | "sats" | "lamports",
    "tx_count": N,
    "latest_timestamp": 1234567890,
    "transactions": [...]
  }

Your job:
- Give the user a clear summary of:
    * which chain the address is on,
    * the current native balance,
    * how many recent transactions we saw,
    * how recent the last activity is (roughly),
    * 1-3 example transactions (direction + approximate size),
- For BTC/SOL, you usually only have txid and time; describe confirmed vs unconfirmed.
- Keep it concise (under ~250 words).
- Do NOT provide financial advice; only describe activity.
"""

blockchain_summary_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="blockchain_summary_agent",
    instruction=SUMMARY_INSTRUCTION,
    description="Summarizes recent activity and balance for a scanned address.",
)


blockchain_checker_agent = SequentialAgent(
    name="blockchain_checker_agent",
    description=(
        "Sequential pipeline that scans blockchain addresses (EVM, Bitcoin, Solana) "
        "and summarizes the results including balance, transaction history, and recent activity."
    ),
    sub_agents=[
        blockchain_scan_agent,
        blockchain_summary_agent,
    ],
)
