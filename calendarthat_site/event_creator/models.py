from django.db import models
from django.conf import settings

import uuid

# Event model
# Represents an event with details like:
# - Associated user (custom user model)
# - Processing status (STARTED, DONE, FAILED)
# - Creation start datetime (build_start) and duration (build_time)
# - Event details: start/end datetime, location, summary, and description
# Uses UUID as the primary key and orders by creation datetime (descending).

class Event(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    
    custom_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events",
    )    

    STARTED = "STARTED"
    DONE = "DONE"
    FAILED = "FAILED"
    BUILD_STATUS_CHOICES = {
        STARTED: "STARTED",
        DONE: "DONE",
        FAILED: "FAILED",
    }

    build_status = models.CharField(
        max_length=7,
        choices=BUILD_STATUS_CHOICES,
        default=STARTED,
    )

    build_start = models.DateTimeField(auto_now_add=True)
    
    build_time = models.DurationField(
        null=True,
        blank=True,
    )    

    user_input = models.TextField()

    date_start = models.DateTimeField(
        null=True,
        blank=True,
    )    

    date_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Event end date and time."
    )

    summary = models.CharField(
        null=True,
        blank=True,
        max_length=255,
    )
    
    location = models.CharField(
        null=True,
        blank=True,
        max_length=255,
    )
    
    description = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.summary} ({self.uuid})"
    
    class Meta:
        ordering = ["-build_start"]
        verbose_name = "Event"
        verbose_name_plural = "Events"