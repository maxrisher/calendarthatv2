# CalendarThat API Documentation

## Overview
CalendarThat provides a RESTful API for creating calendar events from natural language text and retrieving them in multiple formats. The API supports both authenticated and anonymous users, with authenticated users benefiting from timezone-aware event creation.

## Endpoints

### Create Event
`POST /create/`

Creates a new calendar event from natural language text and begins asynchronous processing.

**Request Body:**
```json
{
    "event_text": "Lunch with Sarah next Tuesday at 1pm at Cafe Luna"
}
```

**Success Response (200):**
```json
{
    "event_uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Notes:**
- For authenticated users, the user's timezone will be used for event creation
- For anonymous users, events will be created without timezone information
- Processing happens asynchronously; use the returned UUID to check status

### Check Event Status
`GET /event_status/?event_uuid={uuid}`

Checks the processing status of a previously created event.

**Parameters:**
- `event_uuid`: UUID of the event (required)

**Success Response (200):**
```json
{
    "build_status": "STARTED|DONE|FAILED"
}
```

**Notes:**
- Status will be one of three values:
  - `STARTED`: Initial state, processing in progress
  - `DONE`: Processing completed successfully
  - `FAILED`: Processing failed

### Download Calendar Event
`GET /download/?event_uuid={uuid}`

Retrieves calendar event data in multiple formats.

**Parameters:**
- `event_uuid`: UUID of the event (required)

**Success Response (200):**
```json
{
    "gcal_link": "https://calendar.google.com/calendar/render?action=TEMPLATE&...",
    "outlook_link": "https://outlook.live.com/calendar/0/deeplink/compose?...",
    "ics_data": "BEGIN:VCALENDAR\nVERSION:2.0\n..."
}
```

**Response Fields:**
- `gcal_link`: Direct link to add event to Google Calendar
- `outlook_link`: Direct link to add event to Outlook Calendar
- `ics_data`: Raw iCalendar format data (RFC 5545 compliant)

### Build multiple events
- different endpoint
- gives you back a builder UUID

### Check status of event build
- same status checks, will offer more error explanations

### Download multiple events
- same use uuid to download
- get a list of event objects not just one event back

## Technical Notes
- All endpoints currently support anonymous access
- Events are processed asynchronously to handle potential LLM processing delays
- The API follows RESTful principles and communicates using JSON
- Calendar data is provided in multiple formats to support various client implementations
- Authenticated users' events are associated with their account and use their timezone
- The API currently does not implement rate limiting, but it will be added in the future for anonymous users

