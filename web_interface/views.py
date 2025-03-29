import uuid
import asyncio
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from multiple_event_creator.event_builder_model import EventBuilder
from multiple_event_creator.event_model import Event

logger = logging.getLogger(__name__)

async def home(request):
    """
    [INTERFACE] Renders the web application's home page
    [IN] HTTP request
    [OUT] Rendered home page template
    """
    user = await request.auser()
    return render(request, 'web_interface/home.html', {'user': user})

async def create_events_web(request):
    """
    [INTERFACE] Initiates asynchronous calendar event creation process
    [IN] HTTP POST request with event_text and optional authenticated user
    [OUT] JSON response with event builder UUID for tracking
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

    logger.info(f"New events build requested by user {user.id if user.is_authenticated else 'anonymous'}")
    
    event_builder_uuid = uuid.uuid4()

    event_builder = await EventBuilder.objects.acreate(
        uuid=event_builder_uuid, 
        custom_user=user if user.is_authenticated else None, 
        user_input_text=event_text
        )

    asyncio.create_task(event_builder.build())
    
    logger.info(f"Event builder made with UUID: {event_builder_uuid}")
    
    return JsonResponse({
        "event_builder_uuid": str(event_builder_uuid)
    })

@csrf_exempt # NB: Mallicious websites will be able to make requests through our users to this endpoint
async def get_event_builder_status(request):
    """
    [INTERFACE] Retrieves current status of event builder
    [IN] HTTP GET request with event_builder_uuid
    [OUT] JSON response with event builder build_status (STARTED/DONE/FAILED/NOT_FOUND) and optionally the fail reason
    """
    try:
        event_builder_uuid = uuid.UUID(request.GET.get('event_builder_uuid'))
        event_builder = await EventBuilder.objects.aget(uuid=event_builder_uuid)
        
        response_data = {"event_builder_status": event_builder.build_status}
        if event_builder.build_status == EventBuilder.FAILED and event_builder.build_fail_reason:
            response_data["event_builder_fail_reason"] = event_builder.build_fail_reason
            
        return JsonResponse(response_data)
        
    except EventBuilder.DoesNotExist:
        return JsonResponse({
            "event_builder_status": "NOT_FOUND"
        }, status=404)

@csrf_exempt # NB: Mallicious websites will be able to make requests through our users to this endpoint
async def download_multiple_events(request):
    """
    [INTERFACE] Provides calendar event download data for all created events if processing complete
    [IN] HTTP GET request with event_builder_uuid
    [OUT] JSON response with calendar links (Google Calendar, Outlook) and ICS data, or error if not ready
    """
    try:
        event_builder_uuid = uuid.UUID(request.GET.get('event_builder_uuid'))
        event_builder = await EventBuilder.objects.aget(uuid=event_builder_uuid)
        
        if event_builder.build_status == EventBuilder.STARTED:
            return JsonResponse({
                "error": "Event builder still processing" 
            }, status=409)
            
        if event_builder.build_status == EventBuilder.FAILED:
            return JsonResponse({
                "error": "Event builder failed"
            }, status=422)
            
        events = await Event.objects.filter(builder=event_builder).all()
        events_data = [event.to_dict() for event in events]
        
        return JsonResponse(events_data, safe=False)
    
    except EventBuilder.DoesNotExist:
        return JsonResponse({
            "error": "Event builder not found"
        }, status=404)
    
    except Exception as e:
        logger.error(f"Unexpected error in download_multiple_events: {str(e)}")
        return JsonResponse({
            "error": "Unexpected error occured"
        }, status=500)