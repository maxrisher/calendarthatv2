from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class EmailEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_email_endpoint(self):
        # Sample form data matching the structure from the logs
        form_data = {
            'subject': [''],
            'from': ['Maximus Risher <maximus.risher@gmail.com>'],
            'to': ['new@calendarthat.com'],
            'text': ['Boys trip in last week of may'],
            'html': ['<div dir="ltr">Boys trip in last week of may<br></div>'],
            'headers': ['Content-Type: multipart/alternative; boundary="000000000000f5b072062c2a223d"'],
            'charsets': ['{"to":"UTF-8","from":"UTF-8","subject":"UTF-8","text":"utf-8","html":"utf-8"}'],
            'envelope': ['{"to":["new@calendarthat.com"],"from":"max.risher@gmail.com"}'],
            'attachments': ['0'],
            'sender_ip': ['209.85.219.182']
        }
        
        # Assuming the endpoint is named 'email_receiver' in your urls.py
        url = reverse('create_event_email')
        
        # Make the POST request
        response = self.client.post(url, form_data)
        
        # Basic assertions
        self.assertEqual(response.status_code, 202)  # Or whatever status code you expect
        
        # Add more specific assertions based on your endpoint's behavior
        # For example, if you're creating a calendar event:
        # self.assertTrue(CalendarEvent.objects.filter(title='Boys trip in last week of may').exists())