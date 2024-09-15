import CheckScheduleRelated
import CheckFree
import RespondToEmail
import createEvent
import getCalendarDates
import gmail
import authGoogleCal

def main():
    ## create token
    cal_service, gmail_service = authGoogleCal.authenticate_google_services()

    ## create list of unread emails
    unread = gmail.list_messages(gmail_service)

    i = unread[0]
    print(i.get('id'))
    print(i.get('threadId'))
    encoded = gmail.get_message_content(gmail_service, i.get('threadId'))
    print(encoded)
    content = gmail.get_email_body(encoded)
    if CheckScheduleRelated.IsAppropriate(content, encoded[3]):
        date = encoded[2]
        cal_list = getCalendarDates.get_google_calendar_events(cal_service, date)
        ## if the user is unavailable
        if not (CheckFree.checkFree(content, cal_list, date)):
            username = gmail_service.people().get(resourceName='people/me', personFields='names').execute()
            response = RespondToEmail.generateRescheduleEmail(content, username, cal_list, date, encoded[3])
            gmail.reply_to_email(gmail_service, 'me', i.get('threadId'), response)
        # else:
        #     createEvent.create_google_calendar_event(service, f"Meeting with {encoded[3]}", encoded[2])


if __name__ == '__main__':
    main()
