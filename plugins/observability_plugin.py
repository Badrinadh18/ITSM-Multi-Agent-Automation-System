# plugins/observability_plugin.py
# -------------------------------------------------------------
# ENHANCED OBSERVABILITY PLUGIN (ADK 1.19)
# -------------------------------------------------------------
# Features:
#   ✓ Colorized console logs (cross-platform)
#   ✓ JSONL structured logs (logs/observability.jsonl)
#   ✓ CSV trace logs (logs/observability_trace.csv)
#   ✓ Agent & tool execution timing
#   ✓ Per-agent and per-tool cumulative metrics
#   ✓ ADK 1.19 callback signatures
# -------------------------------------------------------------

import logging
import time
import os
import csv
import json
import platform
from datetime import datetime

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.base_agent import BaseAgent
from google.adk.models.llm_request import LlmRequest


# -------------------------------------------------------------
# COLOR SAFE FOR WINDOWS
# -------------------------------------------------------------
def color(text, c):
    if platform.system() == "Windows":
        return text
    return f"{c}{text}\033[0m"


GREEN = lambda t: color(t, "\033[92m")
YELLOW = lambda t: color(t, "\033[93m")
BLUE = lambda t: color(t, "\033[94m")
MAGENTA = lambda t: color(t, "\033[95m")
CYAN = lambda t: color(t, "\033[96m")
RED = lambda t: color(t, "\033[91m")


# -------------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------------
LOG_DIR = "logs"
JSONL_PATH = os.path.join(LOG_DIR, "observability.jsonl")
CSV_PATH = os.path.join(LOG_DIR, "observability_trace.csv")

os.makedirs(LOG_DIR, exist_ok=True)


# -------------------------------------------------------------
# Initialize CSV header once
# -------------------------------------------------------------
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "event",
            "agent",
            "tool",
            "duration_sec",
            "details"
        ])


# -------------------------------------------------------------
# Helper: append JSONL event
# -------------------------------------------------------------
def log_jsonl(event: dict):
    with open(JSONL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


# -------------------------------------------------------------
# Helper: append CSV event
# -------------------------------------------------------------
def log_csv(event_type, agent=None, tool=None, duration=None, details=""):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            event_type,
            agent,
            tool,
            f"{duration:.4f}" if duration else "",
            details,
        ])


# -------------------------------------------------------------
# ENHANCED PLUGIN
# -------------------------------------------------------------
class ObservabilityPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="observability_plugin")

        self.agent_calls = 0
        self.tool_calls = 0
        self.llm_calls = 0

        self._agent_start = {}
        self._tool_start = {}

        # cumulative metrics
        self.agent_runtime = {}
        self.tool_runtime = {}

        print(GREEN("[PLUGIN:OBS] Enhanced Observability Plugin Loaded."))

    # ---------------------------------------------------------
    # BEFORE AGENT START (ADK 1.19)
    # ---------------------------------------------------------
    async def before_agent_callback(
        self,
        *,
        agent: BaseAgent,
        callback_context: CallbackContext,
        **kwargs
    ):
        self.agent_calls += 1
        self._agent_start[agent.name] = time.time()

        print(BLUE(f"[OBS][AGENT-START] {agent.name} | Call #{self.agent_calls}"))

        # JSONL
        log_jsonl({
            "event": "agent_start",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent.name,
            "invocation_id": callback_context.invocation_id,
        })

    # ---------------------------------------------------------
    # AFTER AGENT END
    # ---------------------------------------------------------
    async def after_agent_callback(
        self,
        *,
        agent: BaseAgent,
        callback_context: CallbackContext,
        result=None,
        **kwargs
    ):
        start = self._agent_start.get(agent.name, None)
        elapsed = time.time() - start if start else 0

        print(GREEN(f"[OBS][AGENT-END] {agent.name} | {elapsed:.3f}s"))

        # update cumulative
        self.agent_runtime[agent.name] = (
            self.agent_runtime.get(agent.name, 0) + elapsed
        )

        # JSONL
        log_jsonl({
            "event": "agent_end",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent.name,
            "duration_sec": elapsed,
        })

        # CSV
        log_csv("agent_end", agent=agent.name, duration=elapsed)

    # ---------------------------------------------------------
    # BEFORE LLM CALL
    # ---------------------------------------------------------
    async def before_model_callback(
        self,
        *,
        callback_context: CallbackContext,
        llm_request: LlmRequest,
        **kwargs
    ):
        self.llm_calls += 1

        print(MAGENTA(
            f"[OBS][LLM-CALL] #{self.llm_calls} | model={llm_request.model}"
        ))

        log_jsonl({
            "event": "llm_call",
            "timestamp": datetime.utcnow().isoformat(),
            "model": llm_request.model,
            "llm_calls": self.llm_calls,
        })

    # =========================================================
    # BEFORE TOOL CALLBACK — UNIVERSAL SAFE VERSION
    # =========================================================
    async def before_tool_callback(
        self,
        *args,
        **kwargs
    ):
        # ADK 1.19 parameters (preferred)
        callback_context = kwargs.get("callback_context")
        tool_name        = kwargs.get("tool_name")
        tool_input       = kwargs.get("tool_input")

        # Fallbacks for older or alternate ADK calls
        tool_kwargs      = kwargs.get("tool_kwargs")
        tool_args        = kwargs.get("tool_args")
        tool             = kwargs.get("tool")

        # Absolute minimum (tool name is required)
        if tool_name is None:
            tool_name = "UNKNOWN_TOOL"

        print(YELLOW(f"[OBS][TOOL-START] {tool_name}"))
        self.tool_calls += 1
        self._tool_start[tool_name] = time.time()

        log_jsonl({
            "event": "tool_start",
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "tool_input": tool_input,
            "tool_args": tool_args,
            "tool_kwargs": tool_kwargs,
        })


    # =========================================================
    # AFTER TOOL CALLBACK — UNIVERSAL SAFE VERSION
    # =========================================================
    async def after_tool_callback(
        self,
        *args,
        **kwargs
    ):
        callback_context = kwargs.get("callback_context")
        tool_name        = kwargs.get("tool_name")
        tool_input       = kwargs.get("tool_input")
        tool_response    = kwargs.get("tool_response")
        tool_kwargs      = kwargs.get("tool_kwargs")
        tool             = kwargs.get("tool")

        if tool_name is None:
            tool_name = "UNKNOWN_TOOL"

        start = self._tool_start.get(tool_name, time.time())
        elapsed = time.time() - start

        print(CYAN(f"[OBS][TOOL-END] {tool_name} | {elapsed:.3f}s"))

        # accumulate runtime
        self.tool_runtime[tool_name] = (
            self.tool_runtime.get(tool_name, 0) + elapsed
        )

        log_jsonl({
            "event": "tool_end",
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "duration_sec": elapsed,
            "response": tool_response,
        })

        log_csv("tool_end", tool=tool_name, duration=elapsed)
