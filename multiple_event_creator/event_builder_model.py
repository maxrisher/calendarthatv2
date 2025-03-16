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
    