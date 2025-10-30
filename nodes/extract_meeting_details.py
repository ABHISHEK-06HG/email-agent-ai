import logging
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field


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


def extract_meeting_details(state: EmailState) -> EmailState:
    parser = JsonOutputParser(pydantic_object=MeetingDetails)

    prompt = PromptTemplate(
        template="""Extract the meeting details from the following email content.
        {format_instructions}
        Email content: {email_content}""",
        input_variables=["email_content"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

    chain = prompt | llm | parser
    time.sleep(5)
    response = chain.invoke({"email_content": state["email_content"]})
    state["meeting_details"] = response
    return state

if __name__ == "__main__":
    sample_email = "From: test@example.example.com\nSubject: Schedule Meeting\nBody: Schedule a team meeting on 2025-10-27 at 10:00 AM IST with user1@example.com, user2@example.com"
    initial_state: EmailState = EmailState(
        email_content=sample_email,
        email_id="test123",
        summary="",
        intent="",
        messages=[],
        meeting_details={},
        meeting_scheduled=False,
        schedule_response="",
    )
    result = extract_meeting_details(initial_state)
    print(f"Final result: {result}")