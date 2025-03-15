from django.db import models

class Event(models.Model):
    uuid
    custom_user
    builder
    built_at
    title
    start_naive
    end_naive
    start_aware
    end_aware
    location
    description
    recurrence_rules
    
    gcal_link
    outlook_link
    ics_data
    