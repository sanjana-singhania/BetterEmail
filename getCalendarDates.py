import datetime
from googleapiclient.discovery import build

def get_google_calendar_events(service, start_date):
    """
    Fetches Google Calendar events from the given start_date to one week out
    and displays them in 12-hour format with AM/PM.

    Args:
        service: Authorized Google Calendar API service instance.
        start_date (str): The starting date in the format 'YYYY-MM-DD'.

    Returns:
        List of events within the next week.
    """
    # Parse the start date and calculate the end date (one week later)
    start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = start_datetime + datetime.timedelta(days=7)

    # Convert to ISO format for Google Calendar API
    time_min = start_datetime.isoformat() + "Z"  # 'Z' indicates UTC time
    time_max = end_datetime.isoformat() + "Z"

    try:
        # Call the Calendar API to fetch events
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return []

        # Print the start time and event summary for each event in 12-hour format with AM/PM
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))

            # If the event has a time, convert to 12-hour format with AM/PM
            if "T" in start:  # It means there's a time component
                start_datetime = datetime.datetime.fromisoformat(start)
                formatted_time = start_datetime.strftime("%I:%M %p, %B %d, %Y")
            else:
                formatted_time = datetime.datetime.strptime(start, "%Y-%m-%d").strftime("%B %d, %Y")
            
            print(f"{formatted_time} - {event['summary']}")

        return events

    except Exception as error:
        print(f"An error occurred: {error}")
        return []

# Example usage:
# Assuming 'service' is already authenticated using OAuth
# get_google_calendar_events(service, "2024-09-14")
