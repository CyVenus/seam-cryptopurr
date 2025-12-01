import random
from typing import Optional, Dict, Any
from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents import LlmAgent

from ..config import DEFAULT_MODEL

def coin_toss(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Returns a fair 50/50 coin toss result.
    Output:
    { "result": "heads" | "tails" }
    """
    result = random.choice(["heads", "tails"])
    return {"result": result}


toss_tool = FunctionTool(
    func=coin_toss,
)


TOSS_AGENT_INSTRUCTION = """
You are the COIN TOSS AGENT.

Your job:

1. ALWAYS call the tool 'coin_toss' to perform the flip.
2. Read the returned JSON:
      { "result": "heads" } OR { "result": "tails" }
3. Then create a short, fun message related to the outcome.

Style:
- Keep it playful and short.
- Examples:
    * "Heads! The universe chooses wisdom today."
    * "Tails! Luck just did a backflip for you."
    * "Heads it is! The crypto gods approve."
    * "Tails! Sometimes fate flips the other way."

Rules:
- DO NOT decide the toss result yourself.
- ALWAYS rely on the tool output.
- Must return:
      the toss output followed by a single quote related to the outcome
"""

toss_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="toss_agent",
    instruction=TOSS_AGENT_INSTRUCTION,
    description="A fun coin-tossing agent with a 50/50 chance of heads or tails.",
    tools=[toss_tool],
)
