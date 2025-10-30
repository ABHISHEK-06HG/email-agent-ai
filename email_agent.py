print("main.py started execution.")
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, List
import operator
import logging

logging.getLogger().setLevel(logging.ERROR)

# Import nodes
from nodes.fetch_latest_email import fetch_latest_email
from nodes.summarize_email import summarize_email
from nodes.detect_intent import detect_intent
from nodes.extract_meeting_details import extract_meeting_details
from nodes.schedule_meeting import schedule_meeting
from nodes.display_summary import display_summary


class AgentState(TypedDict):
    email_content: str
    email_id: str
    summary: str
    intent: Literal["schedule_meeting", "other"]
    meeting_details: dict
    meeting_scheduled: bool
    schedule_response: str
    messages: Annotated[List[BaseMessage], operator.add]


def should_schedule_meeting(state):
    print(f"Intent received by should_schedule_meeting: {state['intent']}")
    # If the intent is to schedule a meeting, proceed to extract details
    if intent == "schedule_meeting":
        return "extract_meeting_details"
    # If the intent is to respond to the email, proceed to draft a response
    elif intent == "respond_email":
        return "draft_response"
    # If the intent is to create a to-do, proceed to create the to-do
    elif intent == "create_todo":
        return "create_todo"
    # If the intent is to summarize the email, proceed to summarize
    elif intent == "summarize_email":
        return "summarize_email"
    # If no specific intent is detected, or for other intents, proceed to a general response
    else:
        return "general_response"


# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("fetch_latest_email", fetch_latest_email)
workflow.add_node("summarize_email", summarize_email)
workflow.add_node("detect_intent", detect_intent)
workflow.add_node("extract_meeting_details", extract_meeting_details)
workflow.add_node("schedule_meeting", schedule_meeting)
workflow.add_node("display_summary", display_summary)

# Set entry point
workflow.set_entry_point("fetch_latest_email")

# Add edges
workflow.add_edge("fetch_latest_email", "summarize_email")
workflow.add_edge("summarize_email", "detect_intent")

# Add conditional edge
workflow.add_conditional_edges(
    "detect_intent",
    should_schedule_meeting,
    {
        "extract_meeting_details": "extract_meeting_details",
        "end": "display_summary",
    },
)

workflow.add_edge("extract_meeting_details", "schedule_meeting")
workflow.add_edge("schedule_meeting", END)
workflow.add_edge("display_summary", END)

# Compile the graph
app = workflow.compile()


if __name__ == "__main__":
    # Example usage:
    # To run the agent, you would typically call app.invoke({}) or app.stream({})
    # For now, let's just print a message indicating the agent is ready.
    print("LangGraph Email Agent pipeline created and ready.")
    print("To run the agent, use: app.invoke({}) or app.stream({})")