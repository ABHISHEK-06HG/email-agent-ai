import base64
import os
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
from utils.google_auth import get_service

def fetch_latest_email(state):
    # print("fetch_latest_email: Dummy execution.")
    # return {"email_content": "Dummy email content"}
    print(f"Entering fetch_latest_email with state: {state}")
    try:
        service = get_service('gmail', 'v1')
        print("Gmail service obtained.")
        # Get the current time and calculate the time 2 minutes ago
        now = datetime.utcnow()
        time_ago = now - timedelta(minutes=2)
        query_time = time_ago.strftime('%Y/%m/%d %H:%M:%S')

        # Search for messages received after query_time
        query = "in:inbox"
        print(f"Searching for emails with query: {query}")
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        print(f"Found {len(messages)} messages.")

        if not messages:
            print("No new emails found in the last 2 minutes.")
            return {"email_content": None, "email_id": None}

        # Get the latest email
        latest_message_id = messages[0]['id']
        print(f"Fetching latest email with ID: {latest_message_id}")
        msg = service.users().messages().get(userId='me', id=latest_message_id, format='full').execute()
        print(f"Email with ID {latest_message_id} fetched.")

        # Extract subject and body
        headers = msg['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
        
        # Get the email body
        parts = msg['payload']['parts']
        body = ""
        for part in parts:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
        
        email_content = f"Subject: {subject}\n\n{body}"
        print(f"Extracted email content (first 200 chars): {email_content[:200]}")
        return {"email_content": email_content, "email_id": latest_message_id}

    except HttpError as error:
        print(f'An error occurred in fetch_latest_email: {error}')
        return {"email_content": None, "email_id": None}
    except Exception as e:
        print(f"An unexpected error occurred in fetch_latest_email: {e}")
        return {"email_content": None, "email_id": None}