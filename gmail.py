from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import EmailInfo
import base64

def list_messages(service):
    """
    List all messages in the user's mailbox that match the query.
    """
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])
        if not messages:
            print('No messages found.')
            return None
        else:
            print(f'Found {len(messages)} messages.')
            return messages
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def get_message_content(service, message_id):
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        headers = message['payload']['headers']
        
        # Extract the 'Date' and 'From' headers
        date = next(header['value'] for header in headers if header['name'] == 'Date')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        
        sender_name = extract_sender_name(sender)
        sender = get_address(sender); 
    
        body = get_email_body(message)
        return EmailInfo(body, date, sender, sender_name)
    except Exception as e:
        print(f'An error occurred: {e}')
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

def create_message(sender, to, subject, body):
    """Create a message to send and encodes it in base64."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    msg = MIMEText(body)
    message.attach(msg)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def reply_to_email(service, user_id, message_id, reply_text):
    """Reply to an email with the given text."""
    # Get the original message
    original_message = service.users().messages().get(userId=user_id, id=message_id).execute()
    
    # Get the original sender's email address
    headers = original_message['payload']['headers']
    from_header = next(header['value'] for header in headers if header['name'] == 'From')
    sender_email = from_header.split('<')[1].strip('>')
    
    # Get the original subject and create a reply subject
    original_subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    reply_subject = 'Re: ' + original_subject
    
    # Create the reply message
    reply_message = create_message(sender_email, sender_email, reply_subject, reply_text)
    
    # Send the reply
    sent_message = service.users().messages().send(userId=user_id, body=reply_message).execute()
    
    print(f"Replied to message ID: {message_id}")
    return sent_message


## helper functions
def decode_base64(data):
    """
    Decode a base64 string (which Gmail API encodes the message body in).
    """
    import base64
    decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
    return decoded_data

def get_address(sender): 
    match = re.search(r'<(.*?)>', sender)
    if match:
        return match.group(1)
    return None

def extract_sender_name(sender):
    # Find the 'From' header
    # Regex to extract the name part before the '<' character
    match = re.match(r'^(.*?)(?:\s<|$)', sender)
    if match:
        return match.group(1).strip()
    return None