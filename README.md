# CalendarThat V2

- event_creator just has the core logic for creating calendar events from text and optional user information. It is not concerned with web requests, network operations etc.
- web_interface just handles the website and has views that call the calendar event creation logic in event_creator. It is not concerned with creating cal events.

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

- (async) event creation view: 
    - User email (optional)
    - Is authenticated (optional)
- Event creation status view: 
    - Is authenticated (optional)
- Event download view: 
    - Is authenticated (optional)

### Event creation workhorse app 
job: performs the core logic for creating calendar events from text and optional user information. It is not concerned with web requests, network operations etc.
- Converts text along with optional user metadata into calendar event objects
- Holds the users: timezone, calendar preferences (gcal vs. apple)
- Holds all past created events: start time, end time, location, etc.