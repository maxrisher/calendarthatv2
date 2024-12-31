# CalendarThat V2
CalendarThat is a web service which aims to convert any 

# Web front end
### User sign up page
### User login page
### Tool page
- Create event: text box and button
- Processing event: fake loading bar
- Download event: buttons for 'apple calendar' 'google calendar' 'outlook calendar' and 'download .ics'

# Back end
### Web interface 
job: has views that call the calendar event creation logic in event_creator. It is not concerned with creating cal events

- (Async) event creation view: 
    - Accepts
        - User email (optional)
        - Is authenticated (optional)
- Event creation status view: 
    - Accepts
        - Is authenticated (optional)
    - Returns
        - status: 'not found', 'processing', 'done'
- Event download view: 
    - Accepts
        - event_id
        - Is authenticated (optional)
    - Returns
        - ical-like JSON
        - Outlook calendar link
        - Gcal link

### Event creation workhorse app 
job: performs the core logic for creating calendar events from text and optional user information. It is not concerned with web requests, network operations etc.
- Converts text along with optional user metadata into calendar event objects
- Holds the users: timezone, calendar preferences (gcal vs. apple)
- Holds all past created events: start time, end time, location, etc.

# Future work / next steps
## Modalities
- Accept email input and output
- Accept WhatsApp input and output
- Accept iOS app input and output

## Input types
- Convert PDFs to calendar events (OCR them, then send them to the core logic)
- Deal with multiple calendar events in the same input (Ask an LLM if more than one event exists in the text, if yes, create many individual events)
- Convert images to calendar events (OCR them to text, then send them to the core logic)