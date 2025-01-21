
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
from asgiref.sync import sync_to_async
import traceback

from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from event_creator.models import Event
from event_creator.llm_caller import LlmCaller

from .utils import raise_if_invalid_ics

logger = logging.getLogger(__name__)

class EventBuilder:
    """
    [INTERFACE] EventBuilder manages the transition from user input to formal calendar event creation in the database
    [IN] event_id and user_input (calendar creation text)
    [OUT] Completes the database version of the user generated calendar event
    """    
    def __init__(self, event_id, user_input):
        # [DATA] the unique event identifier in the database
        self.event_id = event_id
        # [DATA] the user text to create the event
        self.user_input = user_input
        # [DATA] the actual event object in the database which we are building
        self.db_event = None      

    async def formalize(self):
        logger.info(f"Starting event formalization for {self.event_id}")
        
        # self.db_event = await Event.objects.aget(uuid=self.event_id)

        #solution1
        # self.db_event = await Event.objects.select_related('custom_user').aget(uuid=self.event_id)
        # user_timezone_name = self.db_event.custom_user.time_zone_name if self.db_event.custom_user else None

        #solution 2
        # self.db_event = await Event.objects.aget(uuid=self.event_id)
        # custom_user = await CustomUser.objects.aget(id=self.db_event.custom_user_id)
        # user_timezone_name = custom_user.time_zone_name       
        
        #solution 3
        self.db_event = await Event.objects.aget(uuid=self.event_id)
        get_user = sync_to_async(lambda: CustomUser.objects.get(id=self.db_event.custom_user_id))
        custom_user = await get_user()
        user_timezone_name = custom_user.time_zone_name     
        
        #old
        # user_timezone_name = None
        # if self.db_event.custom_user is not None:
        #     user_timezone_name = self.db_event.custom_user.email
        # self.db_event.custom_user.email if self.db_event.custom_user is not None else None
        
        logger.debug(f"tz is: {user_timezone_name}")
        
        try:
            logger.debug(f"Calling LLM for event {self.event_id} with input: {self.user_input[:100]}...")
            llm_caller = LlmCaller()
            await llm_caller.text_to_ics(self.user_input, user_timezone_name)
            
            logger.debug(f"LLM call successful for event {self.event_id}")
            
            self.db_event.start_dttm_aware = llm_caller.response.get('start_dttm_aware', None)
            self.db_event.end_dttm_aware = llm_caller.response.get('end_dttm_aware', None)
            self.db_event.start_dttm_naive = llm_caller.response.get('start_dttm_naive', None)
            self.db_event.end_dttm_naive = llm_caller.response.get('end_dttm_naive', None)
            self.db_event.summary = llm_caller.response.get('summary')
            self.db_event.location = llm_caller.response.get('location')
            self.db_event.description = llm_caller.response.get('description')
            self.db_event.build_status = "DONE"
            self.db_event.build_time = datetime.now(timezone.utc) - self.db_event.build_start
            # await sync_to_async(self.db_event.full_clean)()
            
            raise_if_invalid_ics(
                name=self.db_event.summary,
                begin=self.db_event.start_dttm_aware or self.db_event.start_dttm_naive,
                end=self.db_event.end_dttm_aware or self.db_event.end_dttm_naive,
                description=self.db_event.description,
                location=self.db_event.location
                )
            
            await self.db_event.asave()

        except ValidationError as e:
            self.db_event.build_status = "FAILED"
            logger.info(f"Event validation failed: {self.event_id} - {str(e)}")
            await self.db_event.asave()

        except Exception as e:
            self.db_event.build_status = "FAILED"
            logger.error(f"Unexpected error creating event {self.event_id}: {str(e)}")
            logger.error(f"Full traceback for event {self.event_id}:")
            logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
            await self.db_event.asave()

        logger.info(f"Event {self.event_id} successfully formalized in {self.db_event.build_time}")