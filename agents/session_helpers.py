# agents/session_helpers.py
# -------------------------------------------------------------
# Developer Utility Helpers for Running Sessions Manually
# -------------------------------------------------------------
# These helpers are for debugging, CLI testing, and notebooks.
# They do NOT affect the main ADK pipeline logic.
# -------------------------------------------------------------

from google.genai import types
from agents.app import session_service
import uuid


MODEL_NAME = "gemini-2.5-flash-lite"


async def run_session(
    runner,
    user_queries,
    session_name="default",
):
    """
    Run one or more user messages within a persistent ADK session.
    Includes full debug prints for step-by-step visibility.

    Parameters:
      runner        - ADK Runner (ticket or orchestrator)
      user_queries  - single string or list of strings
      session_name  - unique session identifier
    """

    print("\n============================================================")
    print(f"[SESSION] Starting manual session: '{session_name}'")
    print("============================================================")

    # Convert to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Hard-coded user for dev/debug mode
    USER_ID = "debug_user"

    # ---------------------------------------------------------
    # Create OR Load session
    # ---------------------------------------------------------
    print(f"[SESSION] Preparing DB-backed session for user: {USER_ID}")

    try:
        session = await session_service.create_session(
            app_name=runner.app_name,
            user_id=USER_ID,
            session_id=session_name,
        )
        print("[SESSION] New session created in DB.")

    except Exception:
        session = await session_service.get_session(
            app_name=runner.app_name,
            user_id=USER_ID,
            session_id=session_name,
        )
        print("[SESSION] Existing session loaded from DB.")

    print(f"[SESSION] Using session_id: {session.id}")

    # ---------------------------------------------------------
    # Run messages one by one
    # ---------------------------------------------------------
    for msg in user_queries:
        print("\n------------------------------------------------------------")
        print(f"[SESSION] User > {msg}")
        print("------------------------------------------------------------")

        content = types.Content(role="user", parts=[types.Part(text=msg)])

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        text = part.text.strip()
                        if text and text.lower() != "none":
                            print(f"[{MODEL_NAME}] > {text}")

    print("\n============================================================")
    print("[SESSION] Manual session execution completed.")
    print("============================================================\n")
