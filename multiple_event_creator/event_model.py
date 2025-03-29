import uuid
from urllib.parse import quote
from icalendar import vRecur, Calendar, Event as ICalEvent
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Event(models.Model):
    """
    [INTERFACE] Stores event data and is able to represent itself in the .ics, gcal link, or outlook link formats
    """
    # [DATA] Unique identifier for the event
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # [DATA] Associated user who will own this event, optional
    custom_user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                    on_delete=models.CASCADE,
                                    null=True, 
                                    blank=True, 
                                    related_name="created_events")    
    
    # [DATA] Reference to the builder that created this event
    builder = models.ForeignKey('EventBuilder', on_delete=models.CASCADE, related_name="multiple_events")
    
    # [DATA] When this event was built/created
    built_at = models.DateTimeField()
    
    # [DATA] Event summary
    summary = models.CharField(max_length=255)
    
    # [DATA] Start and end date/datetimes (with and without timezone)
    start_dttm_aware = models.DateTimeField(
        null=True,
        blank=True,
    )    
    start_dttm_naive = models.CharField( # String in ISO 8601 format, e.g. "2025-03-16T13:30"
        max_length=25,
        null=True,
        blank=True,
        )
    start_date = models.DateField(
        null=True,
        blank=True,
    )
    end_dttm_aware = models.DateTimeField(
        null=True,
        blank=True,
    )
    end_dttm_naive = models.CharField( # String in ISO 8601 format, e.g. "2025-03-16T14:30"
        max_length=25,
        null=True,
        blank=True,
        )
    end_date = models.DateField(
        null=True,
        blank=True,
    )
    
    # [DATA] Event details
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    recurrence_rules = models.CharField(max_length=255, blank=True, null=True)
    
    # [DATA] Precomputed calendar links and data
    gcal_link = models.TextField(blank=True, null=True)
    outlook_link = models.TextField(blank=True, null=True)
    ics_data = models.TextField(blank=True, null=True)
    
    @property
    def has_dates(self):
        return self.start_date and self.end_date
    
    @property
    def has_naive_dttms(self):
        return self.start_dttm_naive and self.end_dttm_naive
    
    @property
    def has_aware_dttms(self):
        return self.start_dttm_aware and self.end_dttm_aware
    class Meta:
        ordering = ["-built_at"]
        verbose_name = "Event"
        verbose_name_plural = "Events"
        
    def __str__(self):
        return self.summary
    
    def to_async_safe_dict(self):
        return {
            "uuid": str(self.uuid),
            "summary": self.summary,
            # "builder": self.builder.id if self.builder else None,
            "built_at": self.built_at.isoformat() if self.built_at else None,
            "custom_user": self.custom_user.id if self.custom_user else None,
            
            # Date/time fields
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "start_dttm_aware": self.start_dttm_aware.isoformat() if self.start_dttm_aware else None,
            "end_dttm_aware": self.end_dttm_aware.isoformat() if self.end_dttm_aware else None,
            "start_dttm_naive": self.start_dttm_naive,
            "end_dttm_naive": self.end_dttm_naive,
            
            # Event details
            "location": self.location,
            "description": self.description,
            "recurrence_rules": self.recurrence_rules,
            
            # Generated calendar links
            "gcal_link": self.gcal_link,
            "outlook_link": self.outlook_link,
            "ics_data": self.ics_data,
            
            # Convenience properties
            "has_dates": self.has_dates,
            "has_naive_dttms": self.has_naive_dttms,
            "has_aware_dttms": self.has_aware_dttms,
        }
    
    def clean(self):
        super().clean()
        
        # 1. Validate that date fields don't coexist with datetime fields
        if self.has_dates and (self.has_naive_dttms or self.has_aware_dttms):
            raise ValidationError("Date fields cannot coexist with datetime fields. ")
        
        # 2. Validate that at least one pair of date/time representation exists
        if not (self.has_dates or self.has_naive_dttms or self.has_aware_dttms):
            raise ValidationError("At least one pair of start/end time representation must be present.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def generate_calendar_resources(self):
        """
        [INTERFACE] Generate all calendar resources (outlook link, gcal link, and ICS data)
        [INPUTS] Event details (self)
        [OUTPUTS] Updates self with generated resources
        """
        self.gcal_link = self._generate_gcal_link()
        self.outlook_link = self._generate_outlook_link()
        self.ics_data = self._generate_ics_data()
    
    def _generate_gcal_link(self):
        url_dtstart = ""
        url_dtend = ""
        
        if self.has_dates:
            # Format dates as YYYYMMDD for all-day events
            url_dtstart = self.start_date.strftime("%Y%m%d")
            url_dtend = self.end_date.strftime("%Y%m%d")
        
        elif self.has_aware_dttms:
            # Format timezone-aware datetimes as YYYYMMDDTHHmmssZ
            url_dtstart = self.start_dttm_aware.strftime("%Y%m%dT%H%M%SZ")
            url_dtend = self.end_dttm_aware.strftime("%Y%m%dT%H%M%SZ")
        
        elif self.has_naive_dttms:
            # Use the naive datetime strings, which should already be in the correct format
            url_dtstart = iso_8601_to_ics_dttm(self.start_dttm_naive)
            url_dtend = iso_8601_to_ics_dttm(self.end_dttm_naive)
        
        else:
            raise ValueError("Event must have either dates or datetimes to generate calendar links")
        
        gcal_url = (
            f"https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={quote(self.summary)}"
            f"&dates={url_dtstart}/{url_dtend}"
        )
        
        if self.description:
            gcal_url += f"&details={quote(self.description)}"
            
        if self.location:
            gcal_url += f"&location={quote(self.location)}"
                                
        if self.recurrence_rules:
            gcal_url += f"&recur=RRULE:{quote(self.recurrence_rules)}"
        
        gcal_url += f"&sf=true&output=xml"
        
        return gcal_url
        
    def _generate_outlook_link(self):
        if self.has_dates:
            start_str = self.start_date.strftime("%Y-%m-%d")
            end_str = self.end_date.strftime("%Y-%m-%d")
        
        elif self.has_aware_dttms:
            start_str = self.start_dttm_aware.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = self.end_dttm_aware.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        elif self.has_naive_dttms:
            start_str = self.start_dttm_naive
            end_str = self.end_dttm_naive

        else:
            raise ValueError("Event must have either dates or datetimes to generate calendar links")
        
        outlook_url = (
            f"https://outlook.live.com/calendar/0/deeplink/compose?path=/calendar/action/compose&rru=addevent"
            f"&subject={quote(self.summary)}"
            f"&startdt={start_str}&enddt={end_str}"
            ) 
        
        if self.has_dates:
            outlook_url += "&allday=true"
        
        if self.description:
            outlook_url += f"&body={quote(self.description)}"
        
        if self.location:
            outlook_url += f"&location={quote(self.location)}"
        
        # Note: Outlook web doesn't support recurrence rules in the URL parameters
        
        return outlook_url
        
    def _generate_ics_data(self):
        cal = Calendar()
        cal.add('prodid', '-//CalendarThat//calendarthat.com//')
        cal.add('version', '2.0')
        
        event = ICalEvent()
        event.add('summary', self.summary)
        event.add('uid', str(self.uuid))
        
        event.add('dtstamp', self.built_at)
        
        # Handle different date/time formats
        if self.has_dates:
            # All-day event
            event.add('dtstart', self.start_date)
            event.add('dtend', self.end_date)
        
        elif self.has_aware_dttms:
            # Timezone-aware datetime
            event.add('dtstart', self.start_dttm_aware)
            event.add('dtend', self.end_dttm_aware)
        
        elif self.has_naive_dttms:
            start_dt = datetime.fromisoformat(self.start_dttm_naive)
            end_dt = datetime.fromisoformat(self.end_dttm_naive)
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
        
        if self.description:
            event.add('description', self.description)
        
        if self.location:
            event.add('location', self.location)
        
        if self.recurrence_rules:
            event.add('rrule', vRecur.from_ical(self.recurrence_rules))
        
        cal.add_component(event)
        
        return cal.to_ical().decode('utf-8')
    
def iso_8601_to_ics_dttm(iso_str):
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%Y%m%dT%H%M%S")