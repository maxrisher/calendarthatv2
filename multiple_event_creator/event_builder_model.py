import uuid
import logging
from google import genai
from google.genai import types
from datetime import datetime, timezone

from django.db import models
from django.conf import settings

from .event_model import Event

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
        related_name="events",
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
    
    # [DATA] When event processing started
    build_start = models.DateTimeField(auto_now_add=True)
    
    # [DATA] How long event processing took
    build_time = models.DurationField(
        null=True,
        blank=True,
    )    
    
    # [DATA] Original text input from user
    user_input_text = models.TextField()
    
    llm_raw_response = models.TextField()
    
    class Meta:
        ordering = ["-build_start"]
        verbose_name = "EventBuilder"
        verbose_name_plural = "EventBuilders"
        
    async def build(self):
        user_timezone_name = self.custom_user.time_zone_name if self.custom_user else None
        
        await self._llm_create_events(self.user_input_text, user_timezone_name)
        
        self.build_time = datetime.now(timezone.utc) - self.build_start
        self.build_status = "DONE"
    
    async def _llm_create_events(self, user_input_text, user_timezone_name):
        client = genai.Client(api_key=os.environ.get("PRODUCTION_GEMENI_API_KEY"))
        system_prompt = ""
        user_prompt = ""
        
        self.llm_raw_response = await self.client.aio.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature= 0.1,
            ),
        )
        
        events = self._llm_response_to_events(self.llm_raw_response)
        
        await Event.objects.abulk_create(events)
    
    def _create_llm_user_prompt():
        pass
    
    def _llm_response_to_events(llm_raw_response):
        events = llm_raw_response
        return events
