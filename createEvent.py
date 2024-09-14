import datetime

def create_google_calendar_event(service, event_name, event_date, start_time, end_time, description):
    """
    Creates an event in the Google Calendar.

    Args:
        service: Authorized Google Calendar API service instance.
        event_name (str): The name of the event.
        event_date (str): The date of the event (YYYY-MM-DD).
        start_time (str): Start time of the event (HH:MM, 24-hour format).
        end_time (str): End time of the event (HH:MM, 24-hour format).
        description (str): Description of the event.

    Returns:
        event: The created Google Calendar event.
    """
    
    # Combine event date and times into the right format for Google Calendar
    start_datetime = f"{event_date}T{start_time}:00"
    end_datetime = f"{event_date}T{end_time}:00"

    # Format the event data
    event = {
        'summary': event_name,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'UTC',  # Adjust this as per the user's time zone
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'UTC',  # Adjust this as per the user's time zone
        },
    }

    # Create the event using the Google Calendar API
    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result.get('htmlLink')}")
        return event_result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
# Assuming 'service' is already authenticated using the OAuth flow
# create_google_calendar_event(service, "Meeting", "2024-09-20", "09:00", "10:00", "Team sync meeting")
