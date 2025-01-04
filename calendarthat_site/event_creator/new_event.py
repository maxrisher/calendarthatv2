
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
from datetime import datetime, timezone
import zoneinfo
import asyncio

from event_creator.models import Event

class NewEvent:
    #get the event from our database
    def __init__(self, event_id, user_input):
        self.event_id = event_id
        self.user_input = user_input
        self.db_event = None      

    async def formalize(self):
        print("Started task: ", str(self.event_id)[:5])
        self.db_event = await Event.objects.aget(uuid=self.event_id)        
        await asyncio.sleep(5)
        
        # Create an LLMCaller
        # llm_caller = LlmCaller()
        # Ask our LLMCaller to .text_to_ics(self.user_input)
        # llm_caller.text_to_ics(self.user_input, self.timezone_name)
        # self.date_start = llm_caller.response.get('date_start')
        # ...
        
        # The in-memory event effects
        self.db_event.date_start = datetime(2025, 1, 1, 13, 0, tzinfo=zoneinfo.ZoneInfo("America/Los_Angeles"))
        self.db_event.date_start = datetime(2025, 1, 1, 14, 0, tzinfo=zoneinfo.ZoneInfo("America/Los_Angeles"))
        self.db_event.summary = "Lunch at your mom's house"
        self.db_event.location = "London SW1A 1AA, United Kingdom"
        self.db_event.description = "An outstanding afternoon tea"
        self.db_event.build_status = "DONE"
        self.db_event.build_time = datetime.now(timezone.utc) - self.db_event.build_start

        await self.db_event.asave()
        print("Done with task: ", str(self.event_id)[:5])
