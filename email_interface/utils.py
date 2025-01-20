from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import os
import asyncio
import logging
import base64
from pathlib import Path
from datetime import datetime
import re

from django.conf import settings

from event_creator.models import Event
from .models import Email

logger = logging.getLogger(__name__)

async def send_and_save_event_reply(uuid, destination_email, original_subject, original_message_id):
    event = await Event.objects.aget(uuid=uuid)
    sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
    
    template_email = (settings.BASE_DIR / 'email_interface' / 'new_event_email_template.html').read_text()
    
    email_body = template_email.format(
        gcal_link=event.gcal_link,
        outlook_link=event.outlook_link, 
        summary=event.summary,
        start_datetime=iso_8601_str_to_human_str(event.start_dttm_naive),
        end_datetime=iso_8601_str_to_human_str(event.end_dttm_naive),
        location=event.location
    )
    
    msg_subject = original_subject if original_subject else "Your calendar event"

    msg_to_send = await Email.objects.acreate(subject=msg_subject, 
                        body=email_body, 
                        sender=settings.CALENDARTHAT_EVENT_EMAIL_SENDER_ADDRESS,
                        receiver=destination_email)
    
    try:
        sendgrid_msg = Mail(
            from_email=(msg_to_send.sender, "CalendarThat"),
            to_emails=msg_to_send.receiver,
            subject=msg_to_send.subject,
            html_content=msg_to_send.body,
        )
        
        sendgrid_msg.headers = {
            'In-Reply-To': f"<{original_message_id}>",
            'References': f"<{original_message_id}>",
        }
        
        encoded_file = base64.b64encode(event.ics_data.encode('utf-8')).decode()
        
        attachment = Attachment(
            FileContent(encoded_file),
            FileName('event_from_calendarthat.ics'),
            FileType('text/calendar'),
            Disposition('attachment')
        )
        
        sendgrid_msg.attachment = attachment
        
        await asyncio.to_thread(sg.send, sendgrid_msg)
                
        logger.info(f"email sent! to {destination_email}")
        
    except Exception as e:
        msg_to_send.failed = True
        logger.warning(e)
        await msg_to_send.asave()
        
def iso_8601_str_to_human_str(iso_8601_str):
    dttm = datetime.fromisoformat(iso_8601_str)
    return dttm.strftime("%B %d, %Y at %I:%M %p")

def extract_message_id(headers_str):
    match = re.search(r'Message-ID:\s*<([^>]+)>', headers_str)
    return match.group(1) if match else None