import uuid
import asyncio
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from event_creator.models import Event
from event_creator.new_event import EventBuilder

logger = logging.getLogger(__name__)

def home(request):
    """
    [INTERFACE] Renders the web application's home page
    [IN] HTTP request
    [OUT] Rendered home page template
    """
    return render(request, 'web_interface/home.html')

@csrf_exempt # NB: Mallicious websites will be able to make requests through our users to this endpoint
async def create_event_web(request):
    """
    [INTERFACE] Initiates asynchronous calendar event creation process
    [IN] HTTP POST request with event_text and optional authenticated user
    [OUT] JSON response with event UUID for tracking
    """
    logger.debug(f"""
    Request Method: {request.method}
    Request Path: {request.path}
    Request GET: {request.GET}
    Request POST: {request.POST}
    Request Headers: {dict(request.headers)}
    """)
    user = await request.auser()
    event_text = request.POST.get('event_text', '')

    logger.info(f"New event creation requested by user {user.id if user.is_authenticated else 'anonymous'}")
    
    event_uuid = uuid.uuid4()

    await Event.objects.acreate(
        uuid=event_uuid, 
        custom_user=user if user.is_authenticated else None, 
        user_input=event_text
        )

    new_event = EventBuilder(event_uuid, event_text)
    asyncio.create_task(new_event.formalize())
    
    logger.info(f"Event creation initiated with UUID: {event_uuid}")
    
    return JsonResponse({
        "event_uuid": str(event_uuid)
    })

@csrf_exempt # NB: Mallicious websites will be able to make requests through our users to this endpoint
async def get_event_status(request):
    """
    [INTERFACE] Retrieves current status of event processing
    [IN] HTTP GET request with event_uuid
    [OUT] JSON response with build_status (STARTED/DONE/FAILED) or error
    """
    try:
        event_uuid = uuid.UUID(request.GET.get('event_uuid'))
        event = await Event.objects.aget(uuid=event_uuid)

        return JsonResponse({
            "build_status": event.build_status
        })
        
    except Event.DoesNotExist:
        return JsonResponse({
            "error": "Event not found"
        }, status=404)

@csrf_exempt # NB: Mallicious websites will be able to make requests through our users to this endpoint
async def download_calendar_event(request):
    """
    [INTERFACE] Provides calendar event download data if processing complete
    [IN] HTTP GET request with event_uuid
    [OUT] JSON response with calendar links (Google Calendar, Outlook) and ICS data, or error if not ready
    """
    try:
        event_uuid = uuid.UUID(request.GET.get('event_uuid'))
        event = await Event.objects.aget(uuid=event_uuid)
        
        if event.build_status == Event.STARTED:
            return JsonResponse({
                "error": "Event still processing"
            }, status=409)
            
        if event.build_status == Event.FAILED:
            return JsonResponse({
                "error": "Event processing failed"
            }, status=422)

        return JsonResponse({
            "gcal_link": event.gcal_link,
            "outlook_link": event.outlook_link,
            "ics_data": event.ics_data
        })
    
    except Event.DoesNotExist:
        return JsonResponse({
            "error": "Event not found"
        }, status=404)
    
    except Exception as e:
        logger.error(f"Unexpected error in download_calendar_event: {str(e)}")
        return JsonResponse({
            "error": "Unexpected error occured"
        }, status=500)

async def check_auth(request):
    user = await request.auser()
    
    if user.is_authenticated:
        return JsonResponse({"message": "Authenticated"}, status=200) 
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401) 