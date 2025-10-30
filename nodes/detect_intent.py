from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field
import time


class Intent(BaseModel):
    intent: str = Field(description="The detected intent, either 'schedule_meeting' or 'other'.")


# Define the state
class EmailState(TypedDict):
    email_content: str
    email_id: str
    summary: str
    intent: str
    messages: List[Dict[str, Any]]
    meeting_details: Dict[str, Any]
    meeting_scheduled: bool
    schedule_response: str


def detect_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    prompt = PromptTemplate(
        template="""You are an AI assistant that detects the intent of an email.
        The intent can be either 'schedule_meeting' or 'other'. Respond with only the intent string, e.g., 'schedule_meeting' or 'other'.
        Email: {email_content}""",
        input_variables=["email_content"],
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

    chain = prompt | llm
    time.sleep(5)
    response = chain.invoke({"email_content": state["email_content"]})
    state["intent"] = response.content.strip()
    return state

if __name__ == "__main__":
    sample_email = "From: test@example.com\nSubject: Schedule Meeting\nBody: Please schedule a meeting."
    initial_state: Dict[str, Any] = {
        "email_content": sample_email,
        "email_id": "test123",
        "summary": "",
        "intent": "",
        "messages": [],
        "meeting_details": {},
        "meeting_scheduled": False,
        "schedule_response": "",
    }
    result = detect_intent(initial_state)
    print(f"Final result: {result}")