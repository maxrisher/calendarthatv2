from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Header
import os
import asyncio

from django.conf import settings

from .models import Email

class EmailSender:
    def __init__(self):
        self.send_grid_client = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))

    async def reply(self, subject, body, replying_to_message_id, replying_to_address):
        sendgrid_msg = Mail(
            from_email=settings.CALENDARTHAT_EVENT_EMAIL_SENDER_ADDRESS,
            to_emails=replying_to_address,
            subject=subject,
            plain_text_content=body,
        )
                
        sendgrid_msg.header = Header('In-Reply-To', f'<{replying_to_message_id}>')
        sendgrid_msg.header = Header('References', f'<{replying_to_message_id}>')
        
        #TODO: not sure why we need to add this to thread. why not just await?
        response = await asyncio.to_thread(self.send_grid_client.send, sendgrid_msg)

        await self._save_sent_mail_to_db(subject, body, replying_to_address)

    async def _save_sent_mail_to_db(self, subject, body, receiver):
        await Email.objects.acreate(subject=subject, 
                                    body=body, 
                                    sender=settings.CALENDARTHAT_EVENT_EMAIL_SENDER_ADDRESS,
                                    receiver=receiver)