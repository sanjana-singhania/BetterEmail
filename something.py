import os
import Event
import re
import base64
import dateparser
import requests
from email import message_from_bytes
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Scopes for Gmail and Calendar APIs
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/calendar']
# Baseten API credentials for LLM
MODEL_ID = "8w6yyp2q"
BASETEN_API_KEY = "YMKFudUr.FcjOTi13DlaR3ZtCbBIumoXeqFJy25yx"

def authenticate():
    """Handles OAuth2 authentication and returns service objects for Gmail and Calendar."""
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Load existing credentials from token.json
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials are available, request a login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Create service objects for Gmail and Calendar
    gmail_service = build('gmail', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    return gmail_service, calendar_service

def get_incoming_email(gmail_service):
    """Fetches the latest unread email."""
    results = gmail_service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])
    if not messages:
        print("No new messages.")
        return None
    message_id = messages[0]['id']
    message = gmail_service.users().messages().get(userId='me', id=message_id).execute()
    return message

def extract_email_data(message):
    """Extract sender, recipient, subject, date, and body from the email."""
    headers = message['payload']['headers']
    sender = [header['value'] for header in headers if header['name'] == 'From'][0]
    recipient = [header['value'] for header in headers if header['name'] == 'To'][0]
    subject = [header['value'] for header in headers if header['name'] == 'Subject'][0]
    date = [header['value'] for header in headers if header['name'] == 'Date'][0]
    
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    else:
        body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
    
    return sender, recipient, subject, date, body

def parse_event(data_str):
    lines = data_str.split('\n')
    start_datetime = ""
    end_datetime = ""
    location = ""
    for char in lines[0][16:]:
        start_datetime += char
    for char in lines[1][14:]:
        end_datetime += char
    for char in lines[2][10:]:
        location += char
    p1 = Event.Event(start_datetime, end_datetime, location)
    return p1



def call_llm_for_scheduling_intent(body):
    """
    Calls the Baseten LLM to determine if the email is a scheduling request
    and to extract relevant date and time information.
    """
    url = f"https://model-{MODEL_ID}.api.baseten.co/production/predict"
    headers = {"Authorization": f"Api-Key {BASETEN_API_KEY}"}
    
    # Craft a more specific prompt that emphasizes scheduling-related content
    prompt = [
        {"role": "system", "content": f'''Analyze the following email and determine if it is a scheduling or meeting-related request.
        If it is, extract any date, time, or location information about the meeting. Please format the output as START DATETIME:, END DATEIME:, LOCATION:. PLEASE FORMAT DATES AND TIMES IN ISO FORMAT. IF NO LOCATION IS SPECIFIED, WRITE N/A If it is not related 
        to scheduling, simply respond with 'not schedule-related'.\n\n
        "Email Body:\n{body}'''},
    ]
    
    payload = {
        "messages": prompt,
        "stream": True,
        "max_tokens": 4098,
        "temperature": 0.9
    }
    
    # Send the request to the LLM API
    response = requests.post(url, headers=headers, json=payload, stream=False)
    
    a = ""
    for content in response.iter_content():
        a += content.decode('utf-8')
    print(a)
    event = parse_event(a)
    print(event)
    return event


def find_available_time(calendar_service, start_time, duration=60):
    """Checks Google Calendar availability and returns a suitable time slot."""
    time_min = start_time.isoformat() + 'Z'
    time_max = (start_time + timedelta(days=1)).isoformat() + 'Z'

    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    available_start_time = start_time
    for event in events:
        event_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
        event_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
        if available_start_time + timedelta(minutes=duration) <= event_start:
            return available_start_time
        available_start_time = max(available_start_time, event_end)
    
    return available_start_time

def schedule_meeting(calendar_service, start_time, duration=60, summary="Scheduled Meeting"):
    """Schedules a meeting on Google Calendar."""
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': (start_time + timedelta(minutes=duration)).isoformat(), 'timeZone': 'UTC'}
    }
    event = calendar_service.events().insert(calendarId='primary', body=event).execute()
    return event

def send_response_email(gmail_service, sender, recipient, subject, body):
    """Sends a response email."""
    message = f"To: {sender}\r\nSubject: {subject}\r\n\r\n{body}"
    encoded_message = base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")
    
    send_message = {'raw': encoded_message}
    gmail_service.users().messages().send(userId='me', body=send_message).execute()

def main():
    # Authenticate and get the Gmail and Calendar service objects
    gmail_service, calendar_service = authenticate()

    # Fetch the most recent unread email
    email_message = get_incoming_email(gmail_service)
    if not email_message:
        return
    
    # Extract relevant email details
    sender, recipient, subject, date, body = extract_email_data(email_message)
    
    # Call the LLM to check for scheduling intent and date extraction
    llm_output = call_llm_for_scheduling_intent(body)

    ##print(llm_output)

    # Check if LLM detected scheduling request
    if 'is a scheduling' in llm_output:
        print("here")
        # Extract date and time from the LLM's output
        requested_time = dateparser.parse(llm_output.start_datetime)
        if not requested_time:
            send_response_email(gmail_service, sender, recipient, "Unable to parse date", "Could not determine the date and time from your email.")
            return
        
        # Check if that time slot is available in the calendar
        available_time = find_available_time(calendar_service, requested_time)
        if available_time:
            # Schedule the meeting and notify the sender
            create_google_calendar_event(calendar_service, "Scheduled Meeting", llm_output.start_datetime, llm_output.end_datetime, llm_output.location)
            schedule_meeting(calendar_service, available_time)
            send_response_email(gmail_service, sender, recipient, "Meeting Scheduled", f"Your meeting has been scheduled for {available_time}.")
        else:
            send_response_email(gmail_service, sender, recipient, "No Available Time", "No available time slots found.")
    else:
        # No scheduling intent detected by LLM
        send_response_email(gmail_service, sender, recipient, "No Scheduling Request Detected", "Your email doesn't seem to be a scheduling request.")

if __name__ == '__main__':
    main()