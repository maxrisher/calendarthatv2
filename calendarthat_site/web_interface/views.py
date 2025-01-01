from django.shortcuts import render

import uuid
import asyncio

from accounts.models import CustomUser
from event_creator.models import Event
from event_creator.calendar_event import CalendarEvent

def home(request):
    return render(request, 'web_interface/home.html')

async def create_event_web(request):
    user = request.auser
    event_text = request.body
    email = None

    # test if the user is authenticated; get their details if so
    if user.is_authenticated:
        email = user.email
    else:
        pass
    
    event_id = uuid.uuid4

    # create a new event request in the database
    Event.objects.acreate(uuid=event_id, CustomUser=email, user_input=event_text)

    # create and start running an async task to process the request, passing our request id
    new_event = CalendarEvent(event_id, event_text)
    asyncio.create_task(event_text.formalize_event())

    # return the task ID to the user
    return {
        "event_id": str(event_id)
    }

def get_event_status(request):
    # Check on the status of the event

def download_calendar_event(request):
    # Download the calendar event