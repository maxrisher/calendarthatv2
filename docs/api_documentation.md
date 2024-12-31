# CalendarThat API Documentation

## Endpoints

### Create Calendar Event
`POST /api/events/create-without-auth`

Creates a calendar event from natural language text and returns a download URL.

**Request Body:**
```json
{
    "text": "Lunch with Sarah next Tuesday at 1pm at Cafe Luna"
}
```

**Success Response (200):**
```json
{
    "download_url": "/api/events/download/evt_123abc.ics"
}
```
Note that the download url has an ID string in it (evnt_123abc) to identify the calendar event. Hopefully this will make debugging later easier.

**Error Response (400):**
```json
{
    "error": "Could not create calendar event"
}
```

## Technical Notes
- All times in generated .ics files will be created without timezone information to use client local time
- Event IDs in download URLs should be URL-safe
