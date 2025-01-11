import uuid
import urllib.parse
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from .utils import raise_if_invalid_ics

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

    start_dttm_aware = models.DateTimeField(
        null=True,
        blank=True,
    )    

    # in this format YYYY-MM-DDThh:mm:ss
    start_dttm_naive = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        )

    end_dttm_aware = models.DateTimeField(
        null=True,
        blank=True,
    )

    # in this format YYYY-MM-DDThh:mm:ss
    end_dttm_naive = models.CharField(
        max_length=25,
        null=True,
        blank=True,
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

    @property
    def is_aware(self):
        if self.start_dttm_aware is not None and self.end_dttm_aware is not None:
            return True
        else:
            return False

    @property
    def gcal_link(self):
        url_summary = urllib.parse.quote(self.summary)
        url_description = urllib.parse.quote(self.description)
        url_location = urllib.parse.quote(self.location)

        if self.is_aware:
            url_dtstart = self.start_dttm_aware.strftime("%Y%m%dT%H%M%SZ")
            url_dtend = self.end_dttm_aware.strftime("%Y%m%dT%H%M%SZ")
        else:
            start_dttm = datetime.fromisoformat(self.start_dttm_naive)
            end_dttm = datetime.fromisoformat(self.end_dttm_naive)

            url_dtstart = start_dttm.strftime("%Y%m%dT%H%M%S")
            url_dtend = end_dttm.strftime("%Y%m%dT%H%M%S")

        return f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={url_summary}&dates={url_dtstart}/{url_dtend}&details={url_description}&location={url_location}&sf=true&output=xml"

    @property
    def outlook_link(self):
        url_summary = urllib.parse.quote(self.summary)
        url_description = urllib.parse.quote(self.description)
        url_location = urllib.parse.quote(self.location)

        if self.is_aware:
            url_dtstart = self.start_dttm_aware.strftime("%Y-%m-%dT%H:%M:%SZ")
            url_dtend = self.end_dttm_aware.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            start_dttm = datetime.fromisoformat(self.start_dttm_naive)
            end_dttm = datetime.fromisoformat(self.end_dttm_naive)

            url_dtstart = start_dttm.strftime("%Y-%m-%dT%H:%M:%S")
            url_dtend = end_dttm.strftime("%Y-%m-%dT%H:%M:%S")

        return f"https://outlook.live.com/calendar/0/deeplink/compose?subject={url_summary}&body={url_description}&startdt={url_dtstart}&enddt={url_dtend}&location={url_location}"

    @property
    def ics_data(self):
        ics_timestamp = self.build_start.strftime("%Y%m%dT%H%M%SZ")

        if self.is_aware:
            ics_dtstart = self.start_dttm_aware.strftime("%Y%m%dT%H%M%SZ")
            ics_dtend = self.end_dttm_aware.strftime("%Y%m%dT%H%M%SZ")
        else:
            start_dttm = datetime.fromisoformat(self.start_dttm_naive)
            end_dttm = datetime.fromisoformat(self.end_dttm_naive)

            ics_dtstart = start_dttm.strftime("%Y%m%dT%H%M%S")
            ics_dtend = end_dttm.strftime("%Y%m%dT%H%M%S")

        return f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//CalendarThat//calendarthat.com//\nBEGIN:VEVENT\nSUMMARY:{self.summary}\nDTSTART:{ics_dtstart}\nDTEND:{ics_dtend}\nDTSTAMP:{ics_timestamp}\nDESCRIPTION:{self.description}\nLOCATION:{self.location}\nEND:VEVENT\nEND:VCALENDAR"

    def clean(self):
        super().clean()
        
        print('cleaning')
        
        if self.build_status == "DONE":
            try:
                raise_if_invalid_ics(
                    name=self.summary,
                    begin=self.start_dttm_aware or self.start_dttm_naive,
                    end=self.end_dttm_aware or self.end_dttm_naive,
                    description=self.description,
                    location=self.location
                    )
                print('testing if ics')
                
            except Exception as e:
                raise ValidationError(f"Invalid format: {str(e)}")
    
    def __str__(self):
        return f"{self.summary} ({self.uuid})"
    
    class Meta:
        ordering = ["-build_start"]
        verbose_name = "Event"
        verbose_name_plural = "Events"