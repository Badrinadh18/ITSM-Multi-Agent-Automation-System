# agents/orchestrator.py
# -------------------------------------------------------------
# Master router agent with debug prints
# -------------------------------------------------------------

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from agents.setup import LLM
from agents.ticket_agents import (
    intake_agent,
    classifier_agent,
    kb_agent,
    diagnostics_agent,
    service_now_agent,
    escalation_agent,
    status_loop,
    root_ticket_agent,
)

from agents.session_tools import (
    save_userinfo_tool,
    retrieve_userinfo_tool,
    get_user_tickets_tool,
)


# Convert sub-agents to tools
intake_tool = AgentTool(intake_agent)
classifier_tool = AgentTool(classifier_agent)
kb_tool = AgentTool(kb_agent)
diagnostics_tool = AgentTool(diagnostics_agent)
service_now_tool = AgentTool(service_now_agent)
escalation_tool = AgentTool(escalation_agent)
status_loop_tool = AgentTool(status_loop)
full_pipeline_tool = AgentTool(root_ticket_agent)


orchestrator_agent = LlmAgent(
    name="OrchestratorAgent",
    model=LLM(),
    instruction="""
You are the master ITSM Orchestrator.

ALWAYS call retrieve_userinfo_tool first.
If missing → respond only: ask_user_id

Then route:
- pipeline
- kb
- diagnostics
- classify
- status
- intake

Respond ONLY with the routing keyword.
""",
    tools=[
        retrieve_userinfo_tool,
        save_userinfo_tool,
        get_user_tickets_tool,
        intake_tool,
        classifier_tool,
        kb_tool,
        diagnostics_tool,
        service_now_tool,
        escalation_tool,
        status_loop_tool,
        full_pipeline_tool,
    ],
)

print("[ORCHESTRATOR] Loaded OrchestratorAgent.")
