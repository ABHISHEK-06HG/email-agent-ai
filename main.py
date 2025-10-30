from langgraph.graph import StateGraph, END
from nodes.schedule_meeting import EmailState
from nodes.fetch_email import fetch_email
from nodes.summarize_email import summarize_email
from nodes.detect_intent import detect_intent
from nodes.extract_meeting_details import extract_meeting_details
from nodes.fetch_latest_email import fetch_latest_email
from nodes.schedule_meeting import schedule_meeting
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

def build_graph():
    print("Building LangGraph...")
    workflow = StateGraph(EmailState)

    workflow.add_node("fetch_email", fetch_email)
    workflow.add_node("summarize_email", summarize_email)
    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("extract_meeting_details", extract_meeting_details)
    workflow.add_node("schedule_meeting", schedule_meeting)

    workflow.set_entry_point("fetch_email")
    workflow.add_edge("fetch_email", "summarize_email")
    workflow.add_edge("summarize_email", "detect_intent")
    workflow.add_edge("detect_intent", "extract_meeting_details")
    workflow.add_edge("extract_meeting_details", "schedule_meeting")
    workflow.add_edge("schedule_meeting", END)

    print("LangGraph built. Compiling...")
    compiled_graph = workflow.compile()
    print("LangGraph compiled.")
    return compiled_graph

async def run_agent():
    print("Running agent...")
    graph = build_graph()
    latest_email = fetch_latest_email({"email_content": "", "email_id": "", "summary": "", "intent": "", "messages": [], "meeting_details": {}, "meeting_scheduled": False, "schedule_response": ""})

    if latest_email["email_content"] is None or latest_email["email_id"] is None:
        print("No new emails found or an error occurred during fetching. Exiting.")
        return

    initial_state = {
        "email_content": latest_email["email_content"],
        "email_id": latest_email["email_id"],
        "summary": "",
        "intent": "",
        "messages": [],
        "meeting_details": {},
        "meeting_scheduled": False,
        "schedule_response": "",
    }
    print("Invoking graph...")
    result = graph.invoke(initial_state)
    print("Graph invocation completed.")
    print(result)

if __name__ == "__main__":
    print("main.py started execution.")
    asyncio.run(run_agent())