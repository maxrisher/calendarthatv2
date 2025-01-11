
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
import logging

from django.core.exceptions import ValidationError

from event_creator.models import Event
from event_creator.llm_caller import LlmCaller

logger = logging.getLogger(__name__)

class NewEvent:
    #get the event from our database
    def __init__(self, event_id, user_input):
        self.event_id = event_id
        self.user_input = user_input
        self.db_event = None      

    async def formalize(self):
        print("Started task: ", str(self.event_id)[:5])
        self.db_event = await Event.objects.aget(uuid=self.event_id)       
        use_timezone_name = self.db_event.custom_user.email if self.db_event.custom_user is not None else None
        
        try:
            llm_caller = LlmCaller()
            await llm_caller.text_to_ics(self.user_input, use_timezone_name)
            
            self.db_event.start_dttm_aware = llm_caller.response.get('start_dttm_aware', None)
            self.db_event.end_dttm_aware = llm_caller.response.get('end_dttm_aware', None)
            self.db_event.start_dttm_naive = llm_caller.response.get('start_dttm_naive', None)
            self.db_event.end_dttm_naive = llm_caller.response.get('end_dttm_naive', None)
            self.db_event.summary = llm_caller.response.get('summary')
            self.db_event.location = llm_caller.response.get('location')
            self.db_event.description = llm_caller.response.get('description')
            self.db_event.build_status = "DONE"
            self.db_event.build_time = datetime.now(timezone.utc) - self.db_event.build_start
            await self.db_event.asave()

        except ValidationError as e:
            self.db_event.build_status = "FAILED"
            logger.info(f"Event validation failed: {self.event_id} - {str(e)}")
            await self.db_event.asave()

        except Exception as e:
            self.db_event.build_status = "FAILED"
            logger.error(f"Unexpected error creating event {self.event_id}: {str(e)}")
            await self.db_event.asave()

        print("Done with task: ", str(self.event_id)[:5])
