from google import genai
from google.genai import types
import os
import logging
import json
from jsonschema import validate

from django.utils import timezone

from .event_schema import SHORT_LLM_EVENT_OUTPUT_SCHEMA

logger = logging.getLogger(__name__)

class LlmCaller:
    """
    [INTERFACE] 
    [IN] 
    [OUT] 
    """
    def __init__(self):
        # [DATA] Client for LLM API calls
        self.client = genai.Client(api_key=os.environ.get("PRODUCTION_GEMENI_API_KEY"))
        # [DATA] Raw XML response from LLM
        self._raw_response = None
        # [DATA] Parsed event data dictionary
        self.response = {}

    async def text_to_ics(self, user_text, user_timezone_name=None):
        """
        [INTERFACE] Convert text to calendar event data
        [INPUTS] Event description text, optional timezone
        [OUTPUTS] Populated self.response dict
        """
        with open('multiple_event_creator/00_system_text_to_multi_ics_v1.txt', 'r') as file:
            system_prompt = file.read()

        user_prompt = self._create_ics_user_prompt(user_text, user_timezone_name)

        llm_response = await self.client.aio.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature= 0,
                response_mime_type= 'application/json'
            ),
        )
        
        self._raw_response = llm_response.text
        
        self.response = json.loads(self._raw_response)
        
        #this will raise a validation error if the LLM output does not meet our format or is too long (more than 10 events)
        validate(self.response, schema=SHORT_LLM_EVENT_OUTPUT_SCHEMA) 

        logger.debug("LLM API call successful")

        logger.debug(f"System prompt: \n{system_prompt}")
        logger.debug(f"User prompt: \n{user_prompt}")
        logger.debug(f"LLM response: \n{self._raw_response}")

    def _create_ics_user_prompt(self, user_text, user_timezone_name):
        """
        [INTERFACE] Formats prompt template with user inputs
        [INPUTS] Event text, timezone
        [OUTPUTS] Formatted prompt string
        """  
        with open('multiple_event_creator/00_user_text_to_multi_ics_v1.txt', 'r') as file:
            blank_user_prompt = file.read()

        #TODO: change this to actual code
        utc_time = timezone.now().strftime('%Y-%m-%dT%H:%M') #NB: this is just to the minutes level of precision #timezone.now().strftime('%Y-%m-%dT%H:%M')

        user_prompt = blank_user_prompt.format(
            utc_time=utc_time,
            user_text=user_text,
            user_timezone_name=user_timezone_name if user_timezone_name is not None else "Not specified"
            )

        return user_prompt

    

# llm_caller = LlmCaller()
# import asyncio
# asyncio.run(llm_caller.text_to_ics(""))
# print(llm_caller.response)