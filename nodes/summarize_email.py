import os
import time
from typing import Dict, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Summarize the following email."),
        ("user", "{email_content}"),
    ]
)

def summarize_email(state: Dict[str, Any]) -> Dict[str, Any]:
    print("Summarizing email...")
    email_content = state["email_content"]
    print(f"Email content for summarization: {email_content[:200]}...")

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)
    print("Before LLM invocation.")
    chain = prompt | llm | StrOutputParser()
    time.sleep(5)
    llm_output = chain.invoke({"email_content": state["email_content"]})
    state["summary"] = llm_output
    print(f"Generated summary: {state['summary']}")
    return state

if __name__ == "__main__":
    sample_email = "From: test@example.com\nSubject: Test Email\nBody: This is a test email content that needs to be summarized."
    initial_state = {
        "email_content": sample_email,
        "email_id": "test123",
        "summary": "",
        "intent": "",
        "messages": [],
        "meeting_details": {},
        "meeting_scheduled": False,
        "schedule_response": "",
    }
    result = summarize_email(initial_state)
    print(f"Final result: {result}")