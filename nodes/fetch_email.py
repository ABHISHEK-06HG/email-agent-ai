from nodes.schedule_meeting import EmailState

def fetch_email(state: EmailState) -> EmailState:
    print("Fetching email...")
    return state