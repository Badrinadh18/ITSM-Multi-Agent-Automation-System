# test/test_system.py
# -------------------------------------------------------------
# Enterprise Integration Test Suite (google-adk 1.19.0)
# -------------------------------------------------------------
# Tests:
#   1. FAISS Vector KB
#   2. Google Search Tool
#   3. Code Executor Tool
#   4. Custom Tools (ticket create/update/status)
#   5. MCP Toolsets (filesystem; shell skipped on Windows)
#   6. Full Ticket Pipeline Agent
#   7. Orchestrator Routing with DB Session
# -------------------------------------------------------------

import asyncio
import os
import sys
import platform

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import InMemoryRunner

# Agents
from agents.setup import LLM
from agents.ticket_agents import root_ticket_agent
from agents.orchestrator import orchestrator_agent

# Tools
from tools.vector_kb import add_kb_document, vector_kb_search
from tools.builtin_tools import google_search_tool, code_executor_tool
from tools.custom_tools import (
    create_ticket_tool,
    check_ticket_status_tool,
    update_ticket_status_tool,
    exit_loop_tool,
)
from tools.mcp_tools import (
    mcp_file_toolset,
    mcp_http_toolset,
    mcp_shell_toolset,
)


# -------------------------------------------------------------
# Helper
# -------------------------------------------------------------
def title(msg: str):
    print("\n" + "=" * 80)
    print("[TEST]", msg)
    print("=" * 80)


async def run_tool_test(tool, payload):
    """
    Runs a tool inside a temporary agent to validate tool execution.
    Works for FunctionTool, MCP toolset, or any ADK tool.
    """
    from google.adk.agents import Agent

    agent = Agent(
        name="TempToolAgent",
        model=LLM(),
        instruction="Use ONLY the given tool and return the result.",
        tools=[tool],
    )

    runner = InMemoryRunner(agent=agent)
    events = await runner.run_debug(payload)

    for e in events:
        if e.content:
            for part in e.content.parts:
                if getattr(part, "function_response", None):
                    return part.function_response.response

    return None


# -------------------------------------------------------------
# TEST 1 — FAISS Vector KB
# -------------------------------------------------------------
async def test_vector_kb():
    title("TEST 1: Vector KB (FAISS + Gemini)")

    print("\n[TEST] Adding document to vector KB...")
    add_res = add_kb_document(
        "After Windows update, VPN authentication may fail due to certificate issues.",
        metadata={"category": "Network", "type": "VPN"},
    )
    print("[TEST] Add Result:", add_res)

    print("\n[TEST] Searching vector KB...")
    search_res = vector_kb_search("VPN authentication failure after update")
    print("[TEST] Search Result:", search_res)


# -------------------------------------------------------------
# TEST 2 — Google Search Tool
# -------------------------------------------------------------
async def test_google_search():
    title("TEST 2: Google Search Tool")

    from google.adk.agents import Agent

    agent = Agent(
        name="GoogleSearchTestAgent",
        model=LLM(),
        instruction="Use google_search tool only.",
        tools=[google_search_tool],
    )

    runner = InMemoryRunner(agent=agent)

    print("\n[TEST] Running search agent...")
    events = await runner.run_debug("Troubleshoot Windows VPN 789 error")

    for e in events:
        if e.content:
            for p in e.content.parts:
                if getattr(p, "text", None):
                    print("[SEARCH RESULT]", p.text)


# -------------------------------------------------------------
# TEST 3 — Code Executor Tool
# -------------------------------------------------------------
async def test_code_executor():
    title("TEST 3: Code Executor Tool")

    code = "result = 5 + 7\nprint('Sum =', result)"

    print("[TEST] Executing Python code...")
    result = await run_tool_test(code_executor_tool, {"code": code})
    print("[TEST] Output:", result)


# -------------------------------------------------------------
# TEST 4 — Custom Tools
# -------------------------------------------------------------
async def test_custom_tools():
    title("TEST 4: Custom Tools (ServiceNow Simulated)")

    print("\n> create_ticket_tool:")
    r1 = create_ticket_tool.func(
        summary="VPN issue",
        priority="P2",
        description="Authentication failing",
    )
    print(r1)

    ticket_id = r1["data"]["ticket_id"]

    print("\n> check_ticket_status_tool:")
    r2 = check_ticket_status_tool.func(ticket_id=ticket_id)
    print(r2)

    print("\n> update_ticket_status_tool:")
    r3 = update_ticket_status_tool.func(
        ticket_id=ticket_id,
        new_status="In Progress",
    )
    print(r3)

    print("\n> exit_loop_tool:")
    r4 = exit_loop_tool.func()
    print(r4)


# -------------------------------------------------------------
# TEST 5 — MCP Toolsets
# -------------------------------------------------------------
async def test_mcp():
    title("TEST 5: MCP Toolsets")

    print("[TEST] Testing MCP File Toolset (filesystem)...")
    res = await run_tool_test(
        mcp_file_toolset,
        "readFile system_logs.txt"
    )
    print("[MCP FILE RESULT]:", res)

    print("\n[TEST] MCP HTTP toolset disabled by default:", mcp_http_toolset)

    if platform.system().lower() == "windows":
        print("\n[TEST] MCP Shell Toolset skipped on Windows.")
    else:
        print("\n[TEST] Testing MCP Shell Toolset...")
        res2 = await run_tool_test(
            mcp_shell_toolset,
            "run echo Hello"
        )
        print("[MCP SHELL RESULT]:", res2)


# -------------------------------------------------------------
# TEST 6 — Full Ticket Pipeline
# -------------------------------------------------------------
async def test_pipeline():
    title("TEST 6: Full TicketAutomationPipeline")

    runner = InMemoryRunner(agent=root_ticket_agent)

    input_msg = """
    After last night's Windows update, my laptop can't connect to the VPN.
    I keep getting authentication failures.
    """

    print("[TEST] Running full pipeline...\n")

    events = await runner.run_debug(input_msg)

    print("\n[PIPELINE] Final Output:")
    for e in events:
        # --- FIX: skip events with no content or no parts ---
        if not e.content or not e.content.parts:
            continue

        for p in e.content.parts:
            if getattr(p, "text", None):
                print(p.text)


# -------------------------------------------------------------
# TEST 7 — Orchestrator with DB Session Routing
# -------------------------------------------------------------
async def test_orchestrator():
    title("TEST 7: Orchestrator Routing (DB-backed Session)")

    from agents.app import get_orchestrator_runner

    user_id = "tester123"
    session_id = f"session-{user_id}"

    runner = get_orchestrator_runner()

    print(f"[TEST] user_id={user_id}, session_id={session_id}")

    msg = "Please create a ticket. My VPN is failing."

    print("\n[TEST] Running orchestrator...")

    events = await runner.run_debug(
        msg,
        user_id=user_id,
        session_id=session_id,
    )

    keyword = None
    for e in events:
        if e.content:
            for p in e.content.parts:
                if getattr(p, "text", None):
                    keyword = p.text.strip()
                    print("[ORCH OUTPUT]", keyword)

    print("[TEST] Routing keyword:", keyword)


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
async def main():
    await test_vector_kb()
    await test_google_search()
    await test_code_executor()
    await test_custom_tools()
    await test_mcp()
    await test_pipeline()
    await test_orchestrator()

if __name__ == "__main__":
    asyncio.run(main())
