from typing import Optional, Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, ToolContext

from ..config import DEFAULT_MODEL
from .helper_func_tools.alert_storage import add_alert, cancel_alert, get_active_alerts
from .helper_func_tools.smtp_tools import send_email
from .helper_func_tools.alert_tools import run_alert_checker_tool



def tool_add_alert(token: str, target: float, direction: str, email: str,
                   tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    add_alert(token, target, direction, email)
    return {"status": "saved"}


def tool_cancel_alert(token: str, tool_context: Optional[ToolContext] = None):
    cancel_alert(token)
    return {"status": "cancelled"}


def tool_list_alerts(tool_context: Optional[ToolContext] = None):
    return {"alerts": get_active_alerts()}


def tool_send_test_email(email: str, tool_context=None):
    send_email(email, "Crypto Alert Test Email", "Your alert system is working!")
    return {"status": "test_email_sent"}


add_alert_tool = FunctionTool(
    func=tool_add_alert,
)

cancel_alert_tool = FunctionTool(
    func=tool_cancel_alert,
)

list_alerts_tool = FunctionTool(
    func=tool_list_alerts,
)

test_email_tool = FunctionTool(
    func=tool_send_test_email,
)



ALERT_AGENT_INSTRUCTIONS = """
You are the Alerts Agent.

User may ask:
- "Set alert for BTC above 70000 and email me xyz@gmail.com"
- "Cancel alert for ETH"
- "Show my alerts"
- "Check alerts now"
- "Test email"

Workflow:
1. When setting an alert:
   - Extract token, target price, direction, and email.
   - Call store_alert tool.
   - Call send_test_email tool.
   - Call run_alert_checker_script tool to scan instantly.

2. When user says "cancel <token>":
   - Call cancel_alert tool.

3. When user says "show alerts":
   - Call list_alerts tool.

4. When user says "check alerts now":
   - Call run_alert_checker_script tool.

Always respond with clear confirmations.
Do not invent prices or alerts yourself.
"""

alerts_agent = LlmAgent(
    model=DEFAULT_MODEL,
    name="alerts_agent",
    instruction=ALERT_AGENT_INSTRUCTIONS,
    description="Sets and manages price alerts for tokens using DB + SMTP + one-shot price checker script.",
    tools=[
        add_alert_tool,
        cancel_alert_tool,
        list_alerts_tool,
        test_email_tool,
        run_alert_checker_tool
    ],
)
