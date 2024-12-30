# CalendarThat V2

- event_creator just has the core logic for creating calendar events from text and optional user information. It is not concerned with web requests, network operations etc.
- web_interface just handles the website and has views that call the calendar event creation logic in event_creator. It is not concerned with creating cal events.