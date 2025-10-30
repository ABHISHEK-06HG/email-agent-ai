import logging
from langgraph.graph import StateGraph, END
from utils.google_auth import get_service
from typing import List, Dict, Any, TypedDict
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import re


class MeetingDetails(BaseModel):
    date: str = Field(description="Date of the meeting")
    time: str = Field(description="Time of the meeting")
    duration: str = Field(description="Duration of the meeting, e.g., \"1 hour\"")
    subject: str = Field(description="Subject of the meeting")


class EmailState(TypedDict):
    email_content: str
    email_id: str
    summary: str
    intent: str
    messages: List[Dict[str, Any]]
    meeting_details: Dict[str, Any]
    meeting_scheduled: bool
    schedule_response: str


def summarize_email(state: Dict[str, Any]) -> Dict[str, Any]:
    from_line = state["email_content"].split("From: ")[1].split("\n")[0]
    subject_line = state["email_content"].split("Subject: ")[1].split("\n")[0]
    state["summary"] = f'Summary: From: {from_line}\nSubject: {subject_line}...'
    return state

# Enhanced detect_intent to detect meeting requests
def detect_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    content = state["email_content"].lower()
    if any(keyword in content for keyword in ["schedule", "meeting", "appointment"]):
        state["intent"] = "schedule_meeting"
        
        # Extract date
        date_match = re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b', state["email_content"], re.IGNORECASE)
        if not date_match:
            date_match = re.search(r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', state["email_content"], re.IGNORECASE)
        if not date_match:
            date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', state["email_content"])
        if not date_match:
            date_match = re.search(r'\b\d{1,2}/\d{1,2}/\d{4}\b', state["email_content"])
        
        # Extract time
        time_match = re.search(r'\b(\d{1,2}(:\d{2})?\s*(AM|PM))\b', state["email_content"], re.IGNORECASE)
        if not time_match:
            time_match = re.search(r'\b(\d{1,2}:\d{2})\s*(a\.m\.|p\.m\.)?\b', state["email_content"], re.IGNORECASE)
        
        # Extract duration
        duration_match = re.search(r'\b(\d+\s+(hour|minute)s?)\b', state["email_content"], re.IGNORECASE)
        
        # Extract subject (using email subject as meeting subject)
        subject_match = re.search(r'Subject:\s*(.*)', state["email_content"], re.IGNORECASE)

        state["meeting_details"] = {
            "date": date_match.group(0) if date_match else "Unknown Date",
            "time": time_match.group(0) if time_match else "Unknown Time",
            "duration": duration_match.group(0) if duration_match else "1 hour",
            "subject": subject_match.group(1).strip() if subject_match else "Meeting"
        }
    else:
        state["intent"] = "other"
    return state

# Your schedule_meeting function
def schedule_meeting(state: Dict[str, Any]) -> Dict[str, Any]:
    print("Inside schedule_meeting function.")
    meeting_details = state["meeting_details"]
    if not meeting_details:
        state["meeting_scheduled"] = False
        state["schedule_response"] = "No meeting details provided."
        return state

    service = get_service('calendar', 'v3')

    # Parse date and time
    try:
        date_str = meeting_details['date']
        time_str = meeting_details['time']

        # Combine date and time strings
        datetime_str = f"{date_str} {time_str}"
        # Normalize a.m./p.m. to AM/PM for consistent parsing
        datetime_str = datetime_str.replace("a.m.", "AM").replace("p.m.", "PM")
        print(f"Attempting to parse datetime string: {datetime_str}")

        try:
            start_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %I:%M %p %Z')
            print(f"Parsed with %Y-%m-%d %I:%M %p %Z: {start_datetime}")
        except ValueError:
            try:
                start_datetime = datetime.strptime(datetime_str, '%B %d, %Y %I:%M %p %Z')
                print(f"Parsed with %B %d, %Y %I:%M %p %Z: {start_datetime}")
            except ValueError:
                try:
                    start_datetime = datetime.strptime(datetime_str, '%d %B %Y %I %p')
                    print(f"Parsed with %d %B %Y %I %p: {start_datetime}")
                except ValueError:
                    try:
                        start_datetime = datetime.strptime(datetime_str, '%d %B %Y %I %P') # Added %P for a.m./p.m. with dots
                        print(f"Parsed with %d %B %Y %I %P: {start_datetime}")
                    except ValueError:
                        # Fallback if timezone is not present in the string
                        start_datetime = datetime.strptime(datetime_str.replace(" IST", ""), '%Y-%m-%d %I:%M %p')
                        print(f"Parsed with %Y-%m-%d %I:%M %p (IST removed): {start_datetime}")

        # Calculate end time based on duration
        duration_str = meeting_details.get('duration', '1 hour')
        duration_value = int(re.search(r'\d+', duration_str).group())
        if "hour" in duration_str:
            end_datetime = start_datetime + timedelta(hours=duration_value)
        elif "minute" in duration_str:
            end_datetime = start_datetime + timedelta(minutes=duration_value)
        else:
            end_datetime = start_datetime + timedelta(hours=1) # Default to 1 hour

        start_time_iso = start_datetime.isoformat()
        end_time_iso = end_datetime.isoformat()

    except Exception as e:
        state["meeting_scheduled"] = False
        state["schedule_response"] = f"Error parsing date/time/duration: {e}"
        return state

    # Extract attendees from email content (simple regex for demonstration)
    attendees = []
    email_addresses = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', state['email_content'])
    for email in email_addresses:
        # Exclude sender and any other unwanted emails
        if email not in ["test@example.com", "user1@example.com", "user2@example.com"]:
            attendees.append({'email': email})

    event = {
        'summary': meeting_details.get('subject', 'New Meeting'),
        'description': state['summary'],
        'start': {
            'dateTime': start_time_iso,
            'timeZone': 'Asia/Kolkata',  # Changed to IST for your region
        },
        'end': {
            'dateTime': end_time_iso,
            'timeZone': 'Asia/Kolkata',  # Changed to IST
        },
        'attendees': attendees,
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    logging.info(f"Attempting to schedule event: {event}")
    print(f"Event to be inserted: {event}")

    try:
        print(f"Event to be inserted: {event}")
        print("Attempting to insert event into Google Calendar...")
        event = service.events().insert(calendarId='primary', body=event).execute()
        print("Event insertion successful.")
        print(f"Scheduled meeting: {event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}")
        state["meeting_scheduled"] = True
        state["schedule_response"] = event.get('htmlLink')
        return state
    except Exception as e:
        print(f"Error scheduling meeting: {e}")
        state["meeting_scheduled"] = False
        state["schedule_response"] = str(e)
        return state

# Clean summary output
def display_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n=== Email Summary ===")
    print(state["summary"])
    if state["meeting_scheduled"]:
        print("Meeting Scheduled: Yes")
        print(f'Meeting Link: {state["schedule_response"]}')
    print("===================\n")
    return state

# Define the graph
def build_graph():
    workflow = StateGraph(Dict[str, Any])
    workflow.add_node("fetch_email", lambda state: state)  # Placeholder
    workflow.add_node("summarize_email", summarize_email)
    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("schedule_meeting", schedule_meeting)
    workflow.add_node("display_summary", display_summary)
    workflow.set_entry_point("fetch_email")
    workflow.add_edge("fetch_email", "summarize_email")
    workflow.add_edge("summarize_email", "detect_intent")
    workflow.add_conditional_edges(
        "detect_intent",
        lambda state: state["intent"],
        {
            "schedule_meeting": "schedule_meeting",
            "other": "display_summary",
        },
    )
    workflow.add_edge("schedule_meeting", "display_summary")
    return workflow.compile()

# Run the agent
def run_agent():
    graph = build_graph()
    initial_state = {
        "email_content": "From: test@example.com\nSubject: Please schedule a meeting on October 27, 2025...",
        "email_id": "test123",
        "summary": "",
        "intent": "",
        "messages": [],
        "meeting_details": {},
        "meeting_scheduled": False,
        "schedule_response": ""
    }
    graph.invoke(initial_state)

if __name__ == "__main__":
    run_agent()