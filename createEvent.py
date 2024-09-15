
def create_google_calendar_event(service, event_name, start_datetime, end_datetime, description):
    # Format the event data
    event = {
        'summary': event_name,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'UTC',  
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'UTC',  
        },
    }

    # Create the event
    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result.get('htmlLink')}")
        return event_result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
