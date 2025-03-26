from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, Header
import os
import asyncio
import logging
import base64
from pathlib import Path
from datetime import datetime
import re
import uuid

from django.conf import settings

from accounts.models import CustomUser
from multiple_event_creator.event_builder_model import EventBuilder
from multiple_event_creator.event_model import Event

from .models import Email
from .email_sender import EmailSender

logger = logging.getLogger(__name__)

async def create_and_send_event(email: Email):
    user = await CustomUser.objects.filter(email=email.sender).afirst()
    logger.info(f"New event creation requested by user {user.id if user else 'anonymous'}")

    try:
        event_builder_uuid = uuid.uuid4()
        
        event_builder = await EventBuilder.objects.acreate(
                uuid=event_builder_uuid, 
                custom_user=user, 
                user_input_text=email.to_string()
            )
            
        logger.info(f"Event builder initiated with UUID: {event_builder_uuid}")
        await event_builder.build()
        await send_and_save_event_reply(event_builder_uuid, email.sender, email.subject, email.message_id)
    except Exception as e:
        logger.error(f"Unexpected error in create_and_send_event: {str(e)}")
        await EmailSender().reply(email.subject, "Sorry, an unexpected error occured", email.message_id, email.sender)

async def send_and_save_event_reply(event_builder_uuid, destination_email, original_subject, original_message_id):
    event_builder = await EventBuilder.objects.aget(uuid=event_builder_uuid)
    events = await Event.objects.filter(builder=event_builder).aorder_by('start_date', 'start_dttm_aware').alist()
    
    sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
    
    master_email_template = (settings.BASE_DIR / 'email_interface' / 'master_new_event_email_template.html').read_text()

    email_body = master_email_template.format(calendar_events_html=events_to_html_text(events))
    
    msg_subject = original_subject if original_subject else "Your calendar event"

    msg_to_send = await Email.objects.acreate(subject=msg_subject, 
                        body=email_body, 
                        sender=settings.CALENDARTHAT_EVENT_EMAIL_SENDER_ADDRESS,
                        receiver=destination_email)
    
    try:
        sendgrid_msg = Mail(
            from_email=(msg_to_send.sender, "CalendarThat"), #email fields want both an address and a display name
            to_emails=msg_to_send.receiver,
            subject=msg_to_send.subject,
            html_content=msg_to_send.body,
        )
        
        sendgrid_msg.header = Header('References', f'<{original_message_id}>')
        sendgrid_msg.header = Header('In-Reply-To', f'<{original_message_id}>')

        sendgrid_msg_w_ics = attach_ics_files(sendgrid_msg, events)
        
        response = await asyncio.to_thread(sg.send, sendgrid_msg_w_ics)
        
        logger.info(response.status_code)
        logger.info(response.body)
        logger.info(response.headers)

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

def events_to_html_text(events):
    event_html_template = (settings.BASE_DIR / 'email_interface' / 'single_event_template.html').read_text()
    
    events_html_text = ""
    
    for event in events:
        description_html = ""
        if event.description:
            description_html = f'<p><strong>Description:</strong> {event.description}</p>'
        
        # Format the event template
        formatted_event = event_html_template.format(
            summary=event.summary,
            start_datetime=event_to_time_text(event, "start"),
            end_datetime=event_to_time_text(event, "end"),
            location=event.location or "No location specified",
            description_html=description_html,
            gcal_link=event.gcal_link,
            outlook_link=event.outlook_link
        )
        
        events_html_text += formatted_event
        
    return events_html_text
    
def event_to_time_text(event, start_or_end):
    if event.has_aware_dttms:
        dt = event.start_dttm_aware if start_or_end == "start" else event.end_dttm_aware
        return dt.strftime("%B %d, %Y at %I:%M %p %Z")
    elif event.has_naive_dttms:
        dt_str = event.start_dttm_naive if start_or_end == "start" else event.end_dttm_naive
        return iso_8601_str_to_human_str(dt_str)
    elif event.has_dates:
        dt = event.start_date if start_or_end == "start" else event.end_date
        return dt.strftime("%B %d, %Y") + " (all day)"
    
def attach_ics_files(sendgrid_msg, events):
    
    for i, event in enumerate(events):
        
        encoded_file = base64.b64encode(event.ics_data.encode('utf-8')).decode()
        safe_summary = re.sub(r'[^\w\-\.]', '_', event.summary)[:30]
        filename = f'event_{i+1}_{safe_summary}.ics' if safe_summary else f'event_{i+1}_from_calendarthat.ics'
            
        attachment = Attachment(
            FileContent(encoded_file),
            FileName(filename),
            FileType('text/calendar'),
            Disposition('attachment')
        )
        
        sendgrid_msg.attachment = attachment
    
    return sendgrid_msg