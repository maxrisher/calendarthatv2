from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import asyncio
import logging

from django.db import transaction
from django.conf import settings

from event_creator.models import Event, Email

logger = logging.getLogger(__name__)

async def send_and_save_event_reply(uuid, destination_email):
    event = Event.objects.aget(uuid=uuid)
    sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))

    with transaction.atomic():    
        msg_to_send = Email.objects.acreate(subject="Your calendar event", 
                            body=f"""
                            Hello!

                            I've created a calendar event based on the email you sent:
                            Event: {event.title}
                            Date: {event.start} to {event.end}
                            Location: {event.location}

                            I've attached the calendar invite (.ics file) to this email. You can
                            open it to add this event to your calendar.

                            Best regards,
                            CalendarThat
                            """, 
                            sender=settings.CALENDARTHAT_EVENT_EMAIL_SENDER_ADDRESS)
        
        sendgun_msg = Mail(
            from_email=msg_to_send.sender,
            to_emails=destination_email,
            subject=msg_to_send.subject,
            plain_text_content=msg_to_send.body,
        )
        
        await asyncio.to_thread(sg.send, sendgun_msg)
                
        logger.info(f"email sent! to {destination_email}")