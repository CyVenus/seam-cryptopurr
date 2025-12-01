# alert_check_script.py

import sys
import os
import requests

# Add project root to path to allow imports when run directly
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up: scripts -> sub_agents -> Seam_CryptoPurr -> Agent dev
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Try relative imports first (when used as module)
    from ..helper_func_tools.alert_storage import get_active_alerts, mark_triggered
    from ..helper_func_tools.smtp_tools import send_email
except ImportError:
    # Fall back to absolute imports (when run directly)
    from Seam_CryptoPurr.sub_agents.helper_func_tools.alert_storage import get_active_alerts, mark_triggered
    from Seam_CryptoPurr.sub_agents.helper_func_tools.smtp_tools import send_email


def get_price(token: str) -> float:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token.lower()}&vs_currencies=usd"
    res = requests.get(url, timeout=10).json()
    return float(list(res.values())[0]["usd"])


def run_alert_check():
    alerts = get_active_alerts()
    if not alerts:
        return {"status": "no-alerts"}

    triggered = []

    for a in alerts:
        token = a["token"]
        target = a["target"]
        direction = a["direction"]
        email = a["email"]

        try:
            price = get_price(token)
        except:
            continue

        hit = (
            price >= target if direction == "above"
            else price <= target if direction == "below"
            else False
        )

        if hit:
            subject = f"ALERT: {token} price hit target!"
            body = (
                f"Your alert for {token} ({direction} {target}) has been triggered.\n"
                f"Current price: ${price}\n"
            )
            send_email(email, subject, body)
            triggered.append(a["id"])

    for alert_id in triggered:
        mark_triggered(alert_id)

    return {"status": "completed", "triggered": triggered}


if __name__ == "__main__":
    print(run_alert_check())
