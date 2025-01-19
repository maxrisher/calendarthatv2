import uuid
import logging
import json
import asyncio

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings

from accounts.models import CustomUser
from event_creator.models import Event
from event_creator.new_event import EventBuilder

from .models import Email
from .utils import send_and_save_event_reply

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
async def receive_email(request):
    """
    [INTERFACE] Webhook endpoint for sendgrid that processes incoming emails to create calendar events
    [IN] HTTP POST request containing email data
    [OUT] HTTP response indicating success/failure in reading the email
    """
    try:
        email_data = request.POST
        envelope = json.loads(email_data.get('envelope'))
        logger.info(email_data)
        email = await Email.objects.acreate(
            sender=envelope.get('from'),
            receiver=settings.CALENDARTHAT_EVENT_EMAIL_SENDER_ADDRESS,
            subject=email_data.get('subject', ''),
            body=email_data.get('text', ''),
        )
        
        asyncio.create_task(create_and_send_event(email))
        
        return JsonResponse({"status": "accepted"}, status=202)
    
    except Exception as e:
        logger.error(f"Unexpected error in event_from_email: {str(e)}")
        
        return JsonResponse({
            "error": "Unexpected error occured"
        }, status=500)

async def create_and_send_event(email: Email):
    user = await CustomUser.objects.filter(email=email.sender).afirst()
    event_uuid = uuid.uuid4()
    
    logger.info(f"New event creation requested by user {user.id if user else 'anonymous'}")
    
    await Event.objects.acreate(
            uuid=event_uuid, 
            custom_user=user, 
            user_input=email.to_string()
        )
    
    new_event = EventBuilder(event_uuid, email.to_string())
    
    logger.info(f"Event creation initiated with UUID: {event_uuid}")
    await new_event.formalize()
    await send_and_save_event_reply(event_uuid, email.sender)