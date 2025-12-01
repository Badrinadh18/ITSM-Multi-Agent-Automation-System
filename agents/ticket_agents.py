# agents/ticket_agents.py
# ----------------------------------------------------------------------
# ITSM Multi-Agent Pipeline (ADK 1.19 Compatible)
# Fully instrumented with debug print statements
# ----------------------------------------------------------------------

from google.adk.agents import Agent, SequentialAgent, LoopAgent
from agents import setup
from agents.session_tools import (
    save_ticket_for_user_tool,
    retrieve_userinfo_tool,
)

LLM = setup.LLM


# ======================================================================
# 1. INTAKE AGENT
# ======================================================================
def intake_debug_print(user_msg, userinfo):
    print("\n" + "=" * 60)
    print("[INTAKE] Input received...")
    print("User message:", user_msg)
    print("Session userinfo:", userinfo)
    print("=" * 60)


intake_agent = Agent(
    name="IntakeAgent",
    model=LLM(),
    instruction="""
You are an ITSM intake agent.

First, call retrieve_userinfo_tool to get the session user.
If not found, set user="Unknown".

Extract structured ticket info. 

Respond ONLY with JSON:
{
  "issue_summary": "...",
  "user": "...",
  "device": "...",
  "urgency_guess": "low | medium | high",
  "full_description": "..."
}
""",
    tools=[retrieve_userinfo_tool],
    output_key="ticket_intake",
)


# ======================================================================
# 2. CLASSIFIER AGENT
# ======================================================================
def classifier_debug_print(ticket_intake):
    print("\n" + "=" * 60)
    print("[CLASSIFIER] Classifying intake JSON...")
    print("Input JSON:", ticket_intake)
    print("=" * 60)


classifier_agent = Agent(
    name="ClassifierAgent",
    model=LLM(),
    instruction="""
Use:
{ticket_intake}

Respond ONLY with JSON:
{
  "category": "Network | Application | Hardware | Access | Other",
  "subcategory": "...",
  "impact": 1 | 2 | 3,
  "priority": "P1 | P2 | P3 | P4",
  "recommended_team": "..."
}
""",
    output_key="ticket_classification",
)


# ======================================================================
# 3. KB AGENT
# ======================================================================
def kb_debug_print(intake, classification):
    print("\n" + "=" * 60)
    print("[KB] Computing knowledge base suggestions...")
    print("Intake:", intake)
    print("Classification:", classification)
    print("=" * 60)


kb_agent = Agent(
    name="KBAgent",
    model=LLM(),
    instruction="""
Use:
Intake: {ticket_intake}
Classification: {ticket_classification}

Respond ONLY JSON:
{
  "kb_match_found": true | false,
  "internal_matches": ["..."],
  "external_insights": ["..."],
  "steps": ["..."]
}
""",
    output_key="kb_suggestions",
)


# ======================================================================
# 4. Diagnostics AGENT
# ======================================================================
def diagnostics_debug_print(intake, classification):
    print("\n" + "=" * 60)
    print("[DIAGNOSTICS] Evaluating if diagnostics are needed...")
    print("Intake:", intake)
    print("Classification:", classification)
    print("=" * 60)


diagnostics_agent = Agent(
    name="DiagnosticsAgent",
    model=LLM(),
    instruction="""
Use:
{ticket_intake}
{ticket_classification}

Respond ONLY JSON:
{
  "diagnostics_required": true | false,
  "commands": [...],
  "notes": "..."
}
""",
    output_key="diagnostics_report",
)


# ======================================================================
# 5. ServiceNowCreatorAgent (simulation)
# ======================================================================
def service_now_debug_print(intake, classification, kb_suggestions, diag):
    print("\n" + "=" * 60)
    print("[SERVICENOW] Creating simulated ServiceNow ticket...")
    print("Intake:", intake)
    print("Classification:", classification)
    print("KB Suggestions:", kb_suggestions)
    print("Diagnostics:", diag)
    print("=" * 60)


service_now_agent = Agent(
    name="ServiceNowCreatorAgent",
    model=LLM(),
    instruction="""
Simulate creation of an ITSM incident.

Use:
{ticket_intake}
{ticket_classification}
{kb_suggestions}
{diagnostics_report}

Generate ticket_id as: INCxxxxxxx

Respond ONLY JSON:
{
  "ticket_id": "INC1234567",
  "category": "...",
  "priority": "...",
  "kb_used": true | false,
  "diagnostics_planned": true | false,
  "human_message": "..."
}
""",
    output_key="ticket_creation_result",
)


# ======================================================================
# 6. SessionSaverAgent
# ======================================================================
def session_saver_debug_print(ticket_id, summary, priority):
    print("\n" + "=" * 60)
    print("[SESSION] Saving ticket into session history...")
    print("Ticket ID:", ticket_id)
    print("Summary:", summary)
    print("Priority:", priority)
    print("=" * 60)


session_saver_agent = Agent(
    name="SessionSaverAgent",
    model=LLM(),
    instruction="""
Your ONLY job is to call save_ticket_for_user_tool.

Use:
{ticket_intake.issue_summary}
{ticket_creation_result.ticket_id}
{ticket_creation_result.priority}

Call save_ticket_for_user_tool with:
  ticket_id
  summary
  status="Created"
  priority
""",
    tools=[save_ticket_for_user_tool],
    output_key="session_save_output",
)


# ======================================================================
# 7. Escalation Agent
# ======================================================================
def escalation_debug_print(data):
    print("\n" + "=" * 60)
    print("[ESCALATION] Checking escalation criteria...")
    print("Classification:", data)
    print("=" * 60)


escalation_agent = Agent(
    name="EscalationAgent",
    model=LLM(),
    instruction="""
Using:
{ticket_classification}

If priority = P1 or P2 → respond EXACTLY "ESCALATE"
Else → respond EXACTLY "NO_ESCALATION"
""",
    output_key="escalation_result",
)


# ======================================================================
# 8. Status Loop
# ======================================================================
def status_checker_debug(ticket_result):
    print("\n" + "=" * 60)
    print("[STATUS] Checking ticket status...")
    print("Ticket creation:", ticket_result)
    print("=" * 60)


status_checker_agent = Agent(
    name="StatusCheckerAgent",
    model=LLM(),
    instruction="""
Input: {ticket_creation_result}

If resolved → RESOLVED
Else → PENDING
""",
    output_key="ticket_status",
)


def status_updater_debug(status):
    print("\n" + "=" * 60)
    print("[STATUS] Updating user on ticket state...")
    print("Status:", status)
    print("=" * 60)


status_updater_agent = Agent(
    name="StatusUpdaterAgent",
    model=LLM(),
    instruction="""
Current status: {ticket_status}

If RESOLVED → "Ticket is resolved. Closing the incident."
Else → "Ticket is still being worked on."
""",
    output_key="ticket_status",
)

status_loop = LoopAgent(
    name="TicketStatusLoop",
    sub_agents=[status_checker_agent, status_updater_agent],
    max_iterations=1,
)


# ======================================================================
# 9. ROOT PIPELINE
# ======================================================================
print("\n[PIPELINE] TicketAutomationPipeline loaded.")

root_ticket_agent = SequentialAgent(
    name="TicketAutomationPipeline",
    sub_agents=[
        intake_agent,
        classifier_agent,
        kb_agent,
        diagnostics_agent,
        service_now_agent,
        session_saver_agent,
        escalation_agent,
        status_loop,
    ],
)
