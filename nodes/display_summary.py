from typing import Dict, Any

def display_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n=== Email Summary ===")
    print(state["summary"])
    if state["meeting_scheduled"]:
        print("Meeting Scheduled: Yes")
        print(f'Meeting Link: {state["schedule_response"]}')
    print("===================\n")
    return state