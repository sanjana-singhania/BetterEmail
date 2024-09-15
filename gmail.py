import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',     # Read access to Gmail
]

def authenticate_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    gmail_service = build('gmail', 'v1', credentials=creds)
    return gmail_service

def list_messages(service, user_id='me', query=''):
    """
    List all messages in the user's mailbox that match the query.
    """
    try:
        results = service.users().messages().list(userId=user_id, q=query).execute()
        messages = results.get('messages', [])
        if not messages:
            print('No messages found.')
        else:
            print(f'Found {len(messages)} messages.')
            return messages
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def get_message_content(service, message_id, user_id='me'):
    try:
        message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
        headers = message['payload']['headers']
        
        # Extract the 'Date' and 'From' headers
        date = next(header['value'] for header in headers if header['name'] == 'Date')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        

        sender = get_address(sender); 
    
        body = get_email_body(message)
        return EmailInfo(headers, body, date, sender)
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def get_address(sender): 
    match = re.search(r'<(.*?)>', sender)
    if match:
        return match.group(1)
    return None


def get_email_body(message):
    """
    Extract the body from the message payload.
    """
    body = ''
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                break
    else:
        body = message['payload']['body']['data']

    return decode_base64(body)

def decode_base64(data):
    """
    Decode a base64 string (which Gmail API encodes the message body in).
    """
    import base64
    import quopri
    decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
    return decoded_data

# Example Usage:
# Authenticate and build Gmail API service
gmail_service = authenticate_gmail_service()

# List messages
messages = list_messages(gmail_service, query='subject:test')

# Example Usage:
if messages:
    # Fetch and print the content of the first message
    message_id = messages[0]['id']
    headers, body, date, sender = get_message_content(gmail_service, message_id)
    
    print('Headers:', headers)
    print('Body:', body)
    print('Date:', date)
    print('Sender:', sender)