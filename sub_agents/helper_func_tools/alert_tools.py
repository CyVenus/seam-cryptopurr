import subprocess
from typing import Optional, Dict, Any
from google.adk.tools import FunctionTool, ToolContext


def run_alert_checker_script(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Runs the one-shot alert checker script.
    """
    import os
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "scripts",
        "alert_check_script.py"
    )
    # Set working directory to project root so imports work
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    result = subprocess.run(
        ["python3", script_path],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


run_alert_checker_tool = FunctionTool(
    func=run_alert_checker_script,
)
