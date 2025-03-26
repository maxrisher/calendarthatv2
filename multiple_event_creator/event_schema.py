SHORT_LLM_EVENT_OUTPUT_SCHEMA = {
    "type": "array",
    "maxItems": 10,
    "items": {
        "type": "object",
        "required": [
            "dtstart",
            "dtend",
            "summary"
        ],
        "properties": {
            "time_zone_name": {
                "type": "string"
            },
            "end_time_zone_name": {
                "type": "string"
            },
            "rrule": {
                "type": "string"
            },
            "dtstart": {
                "type": "string"
            },
            "dtend": {
                "type": "string"
            },
            "summary": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "location": {
                "type": "string"
            }
        },
        "propertyOrdering": ["time_zone_name", "end_time_zone_name", "rrule", "dtstart", "dtend", "summary", "description", "location"]
    }
} 

LLM_EVENT_OUTPUT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "dtstart",
            "dtend",
            "summary"
        ],
        "properties": {
            "time_zone_name": {
                "type": "string",
                "description": "The IANA time zone name to be applied to dtend and dtstart. If this value is provided, dtstart and dtend will be made aware with this time zone. Otherwise, they will default to the time zone on the user's computer."
            },
            "end_time_zone_name": {
                "type": "string",
                "description": "The IANA time zone name to be applied to dtend. (Overrides time_zone_name for dtend)"
            },
            "rrule": {
                "type": "string",
                "description": "Recurrence rule in RFC 5545 iCalendar format specifying frequency (DAILY/WEEKLY/MONTHLY/YEARLY), day patterns, intervals, count limits, and end dates. Examples: 'FREQ=WEEKLY;BYDAY=MO,WE,FR' or 'FREQ=MONTHLY;BYMONTHDAY=15;COUNT=12'."
            },
            "dtstart": {
                "type": "string",
                "description": "The datetime marking the start of the event (ISO 8601 format). Or the date marking the start of a full-day event (YYYY-MM-DD)."
            },
            "dtend": {
                "type": "string",
                "description": "The datetime marking the end of the event (ISO 8601 format). Or the date marking the end of a full-day event (YYYY-MM-DD)."
            },
            "summary": {
                "type": "string",
                "description": "The title of the event."
            },
            "description": {
                "type": "string",
                "description": "A brief, essential description of the event. Should only be used when absolutely necessary (<5% of cases)."
            },
            "location": {
                "type": "string",
                "description": "The location of the event, preferably an exact address."
            }
        },
        "propertyOrdering": ["time_zone_name", "end_time_zone_name", "rrule", "dtstart", "dtend", "summary", "description", "location"]
    }
} 