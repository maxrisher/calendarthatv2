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

from multiple_event_creator.event_builder_model import EventBuilder

from .models import Email
from .utils import send_and_save_event_reply, extract_message_id

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
        logger.info(email_data)

        envelope = json.loads(email_data.get('envelope'))

        email = await Email.objects.acreate(
            sender=envelope.get('from'),
            receiver=settings.CALENDARTHAT_EVENT_EMAIL_SENDER_ADDRESS,
            subject=email_data.get('subject', ''),
            body=email_data.get('text', ''),
            message_id=extract_message_id(email_data.get('headers', ''))
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
    logger.info(f"New event creation requested by user {user.id if user else 'anonymous'}")

    event_builder_uuid = uuid.uuid4()
    
    event_builder = await EventBuilder.objects.acreate(
            uuid=event_builder_uuid, 
            custom_user=user, 
            user_input_text=email.to_string()
        )
        
    logger.info(f"Event builder initiated with UUID: {event_builder_uuid}")
    await event_builder.build()
    await send_and_save_event_reply(event_builder_uuid, email.sender, email.subject, email.message_id)