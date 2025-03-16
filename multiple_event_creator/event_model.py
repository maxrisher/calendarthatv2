import uuid
from django.db import models
from django.conf import settings

class Event(models.Model):
    # [DATA] Unique identifier for the event
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # [DATA] Associated user who will own this event, optional
    custom_user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                    on_delete=models.CASCADE,
                                    null=True, 
                                    blank=True, 
                                    related_name="created_events")    
    
    # [DATA] Reference to the builder that created this event
    builder = models.ForeignKey('EventBuilder', on_delete=models.CASCADE, related_name="events")
    
    # [DATA] When this event was built/created
    built_at = models.DateTimeField()
    
    # [DATA] Event summary
    summary = models.CharField(max_length=255)
    
    # [DATA] Start and end dates/times (with and without timezone)
    start_naive = models.DateTimeField()
    end_naive = models.DateTimeField(null=True, blank=True)
    start_aware = models.DateTimeField(null=True, blank=True)
    end_aware = models.DateTimeField(null=True, blank=True)
    
    # [DATA] Event details
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    recurrence_rules = models.CharField(max_length=255, blank=True)
    
    # [DATA] Precomputed calendar links and data
    gcal_link = models.TextField(blank=True)
    outlook_link = models.TextField(blank=True)
    ics_data = models.TextField(blank=True)
    
    class Meta:
        ordering = ["-built_at"]
        verbose_name = "Event"
        verbose_name_plural = "Events"
        
    def __str__(self):
        return self.summary
        
    def generate_calendar_resources(self):
        """
        [INTERFACE] Generate all calendar resources (links and ICS data)
        [INPUTS] Event details (self)
        [OUTPUTS] Updates self with generated resources
        """
        self.gcal_link = self._generate_gcal_link()
        self.outlook_link = self._generate_outlook_link()
        self.ics_data = self._generate_ics_data()
    
    #TODO: check these methods and update them    
    def _generate_gcal_link(self):
        """
        [INTERFACE] Generate Google Calendar link
        [INPUTS] Event details (self)
        [OUTPUTS] URL string for Google Calendar
        """
        # Implementation here
        from urllib.parse import quote
        
        # Format: https://calendar.google.com/calendar/render?action=TEMPLATE&text=summary&dates=YYYYMMDDTHHmmssZ/YYYYMMDDTHHmmssZ
        dates_format = "%Y%m%dT%H%M%SZ"
        
        # Use aware datetimes if available, otherwise naive
        start = self.start_aware or self.start_naive
        end = self.end_aware or self.end_naive or start
        
        # Format start and end dates in the required format
        start_str = start.strftime(dates_format)
        end_str = end.strftime(dates_format)
        
        # Build the URL with parameters
        url = (
            f"https://calendar.google.com/calendar/render"
            f"?action=TEMPLATE"
            f"&text={quote(self.summary)}"
            f"&dates={start_str}/{end_str}"
        )
        
        # Add optional parameters if they exist
        if self.description:
            url += f"&details={quote(self.description)}"
        if self.location:
            url += f"&location={quote(self.location)}"
        
        return url
        
    def _generate_outlook_link(self):
        """
        [INTERFACE] Generate Outlook Calendar link
        [INPUTS] Event details (self)
        [OUTPUTS] URL string for Outlook Calendar
        """
        from urllib.parse import quote
        
        # Use aware datetimes if available, otherwise naive
        start = self.start_aware or self.start_naive
        end = self.end_aware or self.end_naive or start
        
        # Format dates in ISO format
        start_str = start.isoformat()
        end_str = end.isoformat()
        
        # Build the URL with parameters
        url = (
            f"https://outlook.live.com/calendar/0/deeplink/compose"
            f"?subject={quote(self.summary)}"
            f"&startdt={quote(start_str)}"
            f"&enddt={quote(end_str)}"
        )
        
        # Add optional parameters if they exist
        if self.description:
            url += f"&body={quote(self.description)}"
        if self.location:
            url += f"&location={quote(self.location)}"
        
        return url
        
    def _generate_ics_data(self):
        """
        [INTERFACE] Generate iCalendar data
        [INPUTS] Event details (self)
        [OUTPUTS] ICS format string
        """
        import icalendar
        
        cal = icalendar.Calendar()
        cal.add('prodid', '-//Your Company//Event Calendar//EN')
        cal.add('version', '2.0')
        
        event = icalendar.Event()
        event.add('summary', self.summary)
        
        # Use aware datetimes if available, otherwise naive
        start = self.start_aware or self.start_naive
        end = self.end_aware or self.end_naive or start
        
        event.add('dtstart', start)
        event.add('dtend', end)
        
        if self.location:
            event.add('location', self.location)
        if self.description:
            event.add('description', self.description)
        
        # Add UID for the event
        event.add('uid', str(self.uuid))
        
        # Add recurrence rule if it exists
        if self.recurrence_rules:
            event.add('rrule', self.recurrence_rules)
        
        cal.add_component(event)
        return cal.to_ical().decode('utf-8')