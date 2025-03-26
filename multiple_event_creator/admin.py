from django.contrib import admin

from .event_builder_model import EventBuilder
from .event_model import Event

admin.site.register(EventBuilder)
admin.site.register(Event)