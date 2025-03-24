import uuid
import logging
from google import genai
from google.genai import types
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from jsonschema import ValidationError

from django.db import models
from django.conf import settings

from .event_model import Event
from .llm_caller import LlmCaller

logger = logging.getLogger(__name__)

class EventBuilder(models.Model):
    # [DATA] Unique identifier for the event
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    # [DATA] Associated user who created the event, optional
    custom_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_builders",
    )    
    
    # [DATA] Processing status constants
    STARTED = "STARTED"
    DONE = "DONE"
    FAILED = "FAILED"
    BUILD_STATUS_CHOICES = {
        STARTED: "STARTED",
        DONE: "DONE",
        FAILED: "FAILED",
    }

    # [DATA] Current processing status of the event
    build_status = models.CharField(
        max_length=7,
        choices=BUILD_STATUS_CHOICES,
        default=STARTED,
    )
    
    # [DATA] Any reason we might have captured for the event failure, to be shared with the front end
    build_fail_reason = models.CharField(
        null=True,
        blank=True
    )
    
    # [DATA] When event processing started
    build_start = models.DateTimeField(auto_now_add=True)
    
    # [DATA] How long event processing took
    build_time = models.DurationField(
        null=True,
        blank=True,
    )    
    
    # [DATA] Original text input from user
    user_input_text = models.TextField()
    
    llm_raw_response = models.TextField(
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ["-build_start"]
        verbose_name = "EventBuilder"
        verbose_name_plural = "EventBuilders"
        
    async def build(self):
        try:
            user_timezone_name = self.custom_user.time_zone_name if self.custom_user else None
        
            llm_caller = LlmCaller()
            await llm_caller.text_to_ics(self.user_input_text, user_timezone_name)
            self.llm_raw_response = llm_caller._raw_response
            
            events_to_create = []
            
            for event_dict in llm_caller.response:
                django_event = self._event_dict_to_django(event_dict)
                django_event.generate_calendar_resources()
                events_to_create.append(django_event)
            
            await Event.objects.abulk_create(events_to_create)
                                
            self.build_time = datetime.now(timezone.utc) - self.build_start
            self.build_status = "DONE"
            await self.asave()
        
        except ZoneInfoNotFoundError:
            self.build_status = "FAILED"
            self.build_fail_reason = "Invalid timezone."
            logger.error("Event created with invalid timezone.")
            await self.asave()
        
        #if the json returned by the llm is bad
        except ValidationError as validation_error:
            self.build_status = "FAILED"
            
            error_msg = str(validation_error)
            
            if "too long" in error_msg and "maxItems" in error_msg:
                self.build_fail_reason = "Too many events detected. Please limit your request to 10 or fewer events."
            else:
                self.build_fail_reason = f"Invalid event format. Please rephrase your request."
                
            logger.error(f"Validation error in LLM response: {error_msg}")
            await self.asave()

        except Exception as e:
            self.build_status = "FAILED"
            self.build_fail_reason = f"Error: {str(e)}"
            await self.asave()
            logger.error(f"Event build failed: {str(e)}", exc_info=True)
            raise
    
    def _event_dict_to_django(self, event_dict):
        now = datetime.now(timezone.utc)

        dtstart = event_dict.get('dtstart')
        dtend = event_dict.get('dtend')
        time_zone_name = event_dict.get('time_zone_name')
        end_time_zone_name = event_dict.get('end_time_zone_name')

        event_data = {
            'builder': self,
            'custom_user': self.custom_user,
            'built_at': now,
            'summary': event_dict.get('summary', 'Untitled Event'),
            'location': event_dict.get('location', None),
            'description': event_dict.get('description', None),
            'recurrence_rules': event_dict.get('rrule', None),
            
            'start_date': None,
            'end_date': None,
            'start_dttm_naive': None,
            'end_dttm_naive': None,
            'start_dttm_aware': None,
            'end_dttm_aware': None,
        }

        # full-day events
        if len(dtstart) <= 10:  # YYYY-MM-DD format
            event_data['start_date'] = datetime.fromisoformat(dtstart).date()
            event_data['end_date'] = datetime.fromisoformat(dtend).date()
            
        # non-full day events
        else:
            event_data['start_dttm_naive'] = dtstart
            event_data['end_dttm_naive'] = dtend
                    
            # handle timezone-aware events
            if time_zone_name:
                event_data['start_dttm_aware'] = datetime.fromisoformat(dtstart).replace(tzinfo=ZoneInfo(time_zone_name))
                event_data['end_dttm_aware'] = datetime.fromisoformat(dtend).replace(tzinfo=ZoneInfo(time_zone_name))

            # handle events with a different timezone for the end of the event
            if end_time_zone_name:
                event_data['end_dttm_aware'] = datetime.fromisoformat(dtend).replace(tzinfo=ZoneInfo(end_time_zone_name))
        
        django_event = Event(**event_data)
        return django_event