# tools/builtin_tools.py
# -------------------------------------------------------------
# Built-in ADK tools (Google Search + Code Executor)
# Debug print enabled
# -------------------------------------------------------------

from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.function_tool import FunctionTool

print("[TOOLS] Initializing Google Search + Code Executor...")

google_search_tool = google_search


_executor = BuiltInCodeExecutor()


def execute_python(code: str):
    print("\n[TOOL:execute_python] Executing code:\n", code)
    try:
        result = _executor.execute_code({"code": code})
        print("[TOOL:execute_python] Output:", result)
        return {"status": "success", "output": result}
    except Exception as e:
        print("[TOOL:execute_python] Error:", e)
        return {"status": "error", "error": str(e)}


code_executor_tool = FunctionTool(execute_python)

__all__ = ["google_search_tool", "code_executor_tool"]
