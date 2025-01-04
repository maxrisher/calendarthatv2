import uuid
import asyncio

from django.shortcuts import render
from django.http import JsonResponse

from event_creator.models import Event
from event_creator.new_event import NewEvent

def home(request):
    return render(request, 'web_interface/home.html')

async def create_event_web(request):
    user = await request.auser()
    event_text = request.POST.get('event_text', '')
    
    event_uuid = uuid.uuid4()

    # create a new event request in the database
    await Event.objects.acreate(
        uuid=event_uuid, 
        custom_user=user if user.is_authenticated else None, 
        user_input=event_text
        )

    # create and start running an async task to process the request, passing our request id
    new_event = NewEvent(event_uuid, event_text)
    asyncio.create_task(new_event.formalize())

    # return the task ID to the user
    return JsonResponse({
        "event_uuid": str(event_uuid)
    })

async def get_event_status(request):
    # Check on the status of the event
    event_uuid = uuid.UUID(request.GET.get('event_uuid'))
    event = await Event.objects.aget(uuid=event_uuid)

    return JsonResponse({
        "build_status": event.build_status
    })

async def download_calendar_event(request):
    # Download the calendar event
    event_uuid = uuid.UUID(request.GET.get('event_uuid'))
    event = await Event.objects.aget(uuid=event_uuid)
    
    gcal_link = event.gcal_link
    outlook_link = event.outlook_link
    ics_data = event.ics_data

    return JsonResponse({
        "gcal_link": gcal_link,
        "outlook_link": outlook_link,
        "ics_data": ics_data
    })