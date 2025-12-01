# tools/custom_tools.py
# -------------------------------------------------------------
# Custom FunctionTools for ITSM
# Fully ADK-1.19 compatible
# Debug prints added for full visibility
# -------------------------------------------------------------

import uuid
import time
from datetime import datetime
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

from agents.session_tools import save_ticket_for_user


# -------------------------------------------------------------
# 1. CREATE TICKET (ServiceNow simulation)
# -------------------------------------------------------------
def create_ticket(summary: str, priority: str,
                  description: str,
                  tool_context: ToolContext | None = None):

    print("\n[TOOL:create_ticket] Called")
    print("Summary:", summary)
    print("Priority:", priority)
    print("Description:", description)

    ticket_id = f"INC{uuid.uuid4().hex[:7].upper()}"

    response = {
        "status": "success",
        "data": {
            "ticket_id": ticket_id,
            "category": summary,
            "priority": priority,
            "description": description,
            "system": "ServiceNow (simulated)",
        },
    }

    # Save to session if available
    if tool_context:
        print("[TOOL:create_ticket] Saving ticket to session history...")
        try:
            save_ticket_for_user(
                ticket_id=ticket_id,
                summary=summary,
                status="Open",
                priority=priority,
                tool_context=tool_context,
            )
        except Exception as e:
            print("[TOOL:create_ticket] ⚠ Error saving ticket:", e)

    print("[TOOL:create_ticket] Created →", ticket_id)
    return response


# -------------------------------------------------------------
# 2. UPDATE TICKET STATUS
# -------------------------------------------------------------
def update_ticket_status(ticket_id: str, new_status: str,
                         tool_context: ToolContext | None = None):

    print("\n[TOOL:update_ticket_status] Called")
    print("Ticket:", ticket_id, "->", new_status)

    return {
        "status": "success",
        "data": {
            "ticket_id": ticket_id,
            "updated_status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


# -------------------------------------------------------------
# 3. CHECK STATUS
# -------------------------------------------------------------
def check_ticket_status(ticket_id: str,
                        tool_context: ToolContext | None = None):

    print("\n[TOOL:check_ticket_status] Checking status for:", ticket_id)

    return {
        "status": "success",
        "data": {
            "ticket_id": ticket_id,
            "current_status": "In Progress",
        },
    }


# -------------------------------------------------------------
# 4. EXIT LOOP TOOL
# -------------------------------------------------------------
def exit_loop(tool_context: ToolContext | None = None):
    print("\n[TOOL:exit_loop] Exiting loop...")
    return {"status": "resolved", "message": "Ticket resolved."}


# -------------------------------------------------------------
# 5. SAVE LOG TOOL
# -------------------------------------------------------------
def save_log(ticket_id: str, message: str, level: str = "INFO",
             tool_context: ToolContext | None = None):

    print("\n[TOOL:save_log] Log:", ticket_id, message)

    line = f"{datetime.utcnow().isoformat()} | {ticket_id} | {level} | {message}\n"
    with open("system_logs.txt", "a", encoding="utf-8") as f:
        f.write(line)

    return {"status": "success", "data": {"message": "Log saved"}}


# -------------------------------------------------------------
# 6. SCHEDULE STATUS CHECK
# -------------------------------------------------------------
def schedule_status_check(ticket_id: str, delay_seconds: int,
                          tool_context: ToolContext | None = None):

    print("\n[TOOL:schedule_status_check] Scheduled:", ticket_id, delay_seconds)
    time.sleep(0.01)

    return {
        "status": "success",
        "data": {
            "ticket_id": ticket_id,
            "delay_seconds": delay_seconds,
            "scheduled": True,
        },
    }


# -------------------------------------------------------------
# 7. VECTOR SEARCH WRAPPER (placeholder)
# -------------------------------------------------------------
def vector_search(query: str, tool_context=None):
    print("\n[TOOL:vector_search] Vector KB not attached yet.")
    return {"status": "error", "error_message": "Vector KB not attached."}


# -------------------------------------------------------------
# 8. HUMAN APPROVAL TOOL
# -------------------------------------------------------------
def request_human_approval(action: str, reason: str,
                           tool_context: ToolContext):

    print("\n[TOOL:request_human_approval] Action:", action)

    if not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"Approval required: {action}",
            payload={"action": action, "reason": reason},
        )
        return {"status": "pending"}

    if tool_context.tool_confirmation.confirmed:
        return {"status": "success", "data": {"approved": True}}
    else:
        return {"status": "success", "data": {"approved": False}}


# -------------------------------------------------------------
# Wrap tools
# -------------------------------------------------------------
create_ticket_tool = FunctionTool(create_ticket)
update_ticket_status_tool = FunctionTool(update_ticket_status)
check_ticket_status_tool = FunctionTool(check_ticket_status)
exit_loop_tool = FunctionTool(exit_loop)
save_log_tool = FunctionTool(save_log)
schedule_status_check_tool = FunctionTool(schedule_status_check)
vector_search_tool = FunctionTool(vector_search)
request_approval_tool = FunctionTool(request_human_approval)


__all__ = [
    "create_ticket_tool",
    "update_ticket_status_tool",
    "check_ticket_status_tool",
    "exit_loop_tool",
    "save_log_tool",
    "schedule_status_check_tool",
    "vector_search_tool",
    "request_approval_tool",
]
