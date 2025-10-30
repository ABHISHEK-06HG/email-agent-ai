import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from nodes.schedule_meeting import EmailState

load_dotenv()

def summarize_email_standalone():
    state = EmailState(
        email_content="From: test@example.com\nSubject: Please schedule a meeting on October 27, 2025 at 10:00 AM IST with user1@example.com, user2@example.com",
        email_id="test123",
        summary="",
        intent="",
        messages=[],
        meeting_details={},
        meeting_scheduled=False,
        schedule_response="",
    )

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-pro-latest", google_api_key=os.environ.get("GOOGLE_API_KEY"), temperature=0.7, max_output_tokens=200)
        print("Before standalone LLM invocation.")
        summary = ""
        for chunk in llm.stream(f"Summarize the following email: {state.email_content}"):
            summary += chunk.content
        print("After standalone LLM invocation.")
        state.summary = summary
        print(f"Standalone summary: {state.summary}")
    except Exception as e:
        print(f"Error during standalone LLM invocation: {e}")

if __name__ == "__main__":
    summarize_email_standalone()