
#CalEvent
#__init__ requires an event id
# init tries to read in any existing data in the database about the event

# Requires text
# optional user timezone

# stores event start time
# stores event end time
# stores event location

# async formalize_event() method uses a prompt to call an LLM and create a calendar event. 
# 0. First checks to see that its event data has not already been set.
# 1. Send claude 3.5 a prompt with the user text and user timezone
# 2. Extract and set all event properties on its self
# 3. Write event properties to the database object

# to_ical() creates an ical file

# to_gcal_link creates a gcal link

# to_outlook_link creates an outlook link

from event_creator.models import Event
from datetime import datetime, timezone

class CalendarEvent:
    #get the event from our database
    def __init__(self, event_id, user_input):
        self.event_id = event_id
        self.db_event = Event.objects.get(uuid=event_id)
        self.timezone_name = None
        if self.db_event.custom_user is not None:
            self.timezone_name = self.db_event.custom_user.timezone_name

        self.build_start = self.db_event.build_start
        self.user_input = self.db_event.user_input
        # The following are the properties that are set by formalization (ie turning a text event into a formal .ical)
        self.date_start = self.db_event.date_start
        self.date_end = self.db_event.date_end
        self.summary = self.db_event.summary
        self.location = self.db_event.location
        self.description = self.db_event.description

    async def formalize(self):
        await asyncio.sleep(5)
        
        # Create an LLMCaller
        # llm_caller = LlmCaller()
        # Ask our LLMCaller to .text_to_ics(self.user_input)
        # llm_caller.text_to_ics(self.user_input, self.timezone_name)
        # self.date_start = llm_caller.response.get('date_start')
        # ...
        
        # The in-memory event effects
        self.date_start = datetime(2025, 1, 1, 13, 0, tzinfo=timezone.utc),
        self.date_end = datetime(2025, 1, 1, 14, 0, tzinfo=timezone.utc),
        self.summary = "Lunch at your mom's house"
        self.location = "London SW1A 1AA, United Kingdom"
        self.description = "An outstanding afternoon tea"

        # The database effects
        self.db_event.date_start = self.date_start
        self.db_event.date_end = self.date_end
        self.db_event.summary = self.summary
        self.db_event.location = self.location
        self.db_event.description = self.description

        self.db_event.build_status = "DONE"
        self.db_event.build_time = datetime.now(timezone.utc) - self.build_start
