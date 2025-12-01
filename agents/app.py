# agents/app.py
# -------------------------------------------------------------
# ADK Application Wrapper for ITSM System
# - Database-backed sessions
# - Orchestrator-only Web UI usage
# - Debug-friendly prints
# -------------------------------------------------------------

from google.adk.apps.app import App, ResumabilityConfig, EventsCompactionConfig
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.adk.plugins.logging_plugin import LoggingPlugin

from plugins.observability_plugin import ObservabilityPlugin

# Agents
from agents.ticket_agents import root_ticket_agent
from agents.orchestrator import orchestrator_agent


# -------------------------------------------------------------
# Session DB
# -------------------------------------------------------------
DB_URL = "sqlite+aiosqlite:///itsm_sessions.db"
session_service = DatabaseSessionService(db_url=DB_URL)


# -------------------------------------------------------------
# Ticket Pipeline App (USED INTERNALLY)
# -------------------------------------------------------------
ticket_app = App(
    name="itsm_ticket_app",
    root_agent=root_ticket_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
    plugins=[
        LoggingPlugin(),
        ObservabilityPlugin(),
    ],
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,
        overlap_size=2,
    ),
)


# -------------------------------------------------------------
# Orchestrator App (EXPOSED IN WEB UI)
# -------------------------------------------------------------
orchestrator_app = App(
    name="itsm_orchestrator_app",
    root_agent=orchestrator_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
    plugins=[
        LoggingPlugin(),
        ObservabilityPlugin(),
    ],
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=10,
        overlap_size=2,
    ),
)


# -------------------------------------------------------------
# Export runners
# -------------------------------------------------------------
def get_ticket_runner() -> Runner:
    return Runner(app=ticket_app, session_service=session_service)


def get_orchestrator_runner() -> Runner:
    return Runner(app=orchestrator_app, session_service=session_service)


__all__ = [
    "get_ticket_runner",
    "get_orchestrator_runner",
    "session_service",
    "ticket_app",
    "orchestrator_app",
]
