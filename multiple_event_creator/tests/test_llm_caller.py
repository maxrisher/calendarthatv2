from django.test import TestCase
from multiple_event_creator.llm_caller import LlmCaller
import asyncio

class LlmCallerTestCase(TestCase):
    def test_text_to_ics_basic(self):
        llm_caller = LlmCaller()
        asyncio.run(llm_caller.text_to_ics("Team meeting on March 20th at 10am"))
        self.assertIsNotNone(llm_caller.response)