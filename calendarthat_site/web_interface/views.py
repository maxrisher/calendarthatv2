import uuid
import asyncio

from django.shortcuts import render
from django.http import JsonResponse

from accounts.models import CustomUser
from event_creator.models import Event
from event_creator.new_event import NewEvent

def home(request):
    return render(request, 'web_interface/home.html')

async def create_event_web(request):
    user = await request.auser()
    event_text = request.POST.get('event_text', '')
    
    event_id = uuid.uuid4()

    # create a new event request in the database
    await Event.objects.acreate(
        uuid=event_id, 
        custom_user=user if user.is_authenticated else None, 
        user_input=event_text
        )

    # create and start running an async task to process the request, passing our request id
    new_event = NewEvent(event_id, event_text)
    asyncio.create_task(new_event.formalize())

    # return the task ID to the user
    return JsonResponse({
        "event_id": str(event_id)
    })

def get_event_status(request):
    # Check on the status of the event
    return {
        "build_status": "STARTED"
    }

def download_calendar_event(request):
    # Download the calendar event
    return JsonReponse({
        "gcal_link": "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Team+Meeting&dates=20250105T150000Z/20250105T160000Z&details=Discuss+project+milestones+and+set+next+steps.&location=Office+Room+101&sf=true&output=xml",
        "outlook_link": "https://outlook.live.com/calendar/0/deeplink/compose?subject=Team+Meeting&body=Discuss+project+milestones+and+set+next+steps.&startdt=2025-01-05T15:00:00Z&enddt=2025-01-05T16:00:00Z&location=Office+Room+101",
        "ics_data": "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Calendar Event Generator//example.com//\nBEGIN:VEVENT\nSUMMARY:Team Meeting\nDTSTART:20250105T150000Z\nDTEND:20250105T160000Z\nDTSTAMP:20250104T000000Z\nDESCRIPTION:Discuss project milestones and set next steps.\nLOCATION:Office Room 101\nEND:VEVENT\nEND:VCALENDAR"
    })