# agents/session_tools.py
# -------------------------------------------------------------
# Session tools (with debug prints)
# -------------------------------------------------------------

from typing import Dict, Any, List
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext


def save_userinfo(user_id: str, name: str = None,
                  department: str = None,
                  location: str = None,
                  tool_context: ToolContext = None) -> Dict[str, Any]:

    print(f"[SESSION] Saving userinfo: {user_id}, {name}, {department}, {location}")

    state = tool_context.state
    state["user:id"] = user_id
    if name:
        state["user:name"] = name
    if department:
        state["user:department"] = department
    if location:
        state["user:location"] = location

    return {
        "status": "success",
        "message": "User info saved.",
        "data": {
            "id": user_id,
            "name": name,
            "department": department,
            "location": location,
        },
    }


def retrieve_userinfo(tool_context: ToolContext = None):
    data = {
        "id": tool_context.state.get("user:id"),
        "name": tool_context.state.get("user:name"),
        "department": tool_context.state.get("user:department"),
        "location": tool_context.state.get("user:location"),
    }
    print(f"[SESSION] Retrieved userinfo: {data}")
    return {"status": "success", "data": data}


def save_ticket_for_user(ticket_id: str, summary: str,
                         status: str, priority: str,
                         tool_context: ToolContext = None):

    print(f"[SESSION] Saving ticket: {ticket_id}, {summary}, {priority}")

    tickets: List[dict] = tool_context.state.get("user:tickets", [])
    new_ticket = {
        "ticket_id": ticket_id,
        "summary": summary,
        "status": status,
        "priority": priority,
    }

    tickets.append(new_ticket)
    tool_context.state["user:tickets"] = tickets

    return {
        "status": "success",
        "message": "Ticket saved to user history.",
        "ticket": new_ticket,
    }


def get_user_tickets(tool_context: ToolContext = None):
    tickets = tool_context.state.get("user:tickets", [])
    print(f"[SESSION] Retrieved {len(tickets)} tickets.")
    return {"status": "success", "tickets": tickets, "count": len(tickets)}


# Wrap tools
save_userinfo_tool = FunctionTool(save_userinfo)
retrieve_userinfo_tool = FunctionTool(retrieve_userinfo)
save_ticket_for_user_tool = FunctionTool(save_ticket_for_user)
get_user_tickets_tool = FunctionTool(get_user_tickets)


__all__ = [
    "save_userinfo_tool",
    "retrieve_userinfo_tool",
    "save_ticket_for_user_tool",
    "get_user_tickets_tool",
]
