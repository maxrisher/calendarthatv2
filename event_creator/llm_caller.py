from google import genai
from google.genai import types
import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime
import logging

from django.utils import timezone

from .utils import extract_first_xml

logger = logging.getLogger(__name__)

class LlmCaller:
    """
    [INTERFACE] LlmCaller asks an LLM a variety of prompts, which are its methods. Namely, text_to_ics() converts user text into ICS event data.
    [IN] user_text (str), user_timezone_name (str, optional).
    [OUT] self.response (dict) with ICS fields.
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
        with open('event_creator/00_system_text_to_ics_v1.txt', 'r') as file:
            system_prompt = file.read()

        user_prompt = self._create_ics_user_prompt(user_text, user_timezone_name)

        llm_response = await self.client.aio.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature= 0.1,
            ),
        )

        self._raw_response = llm_response.content[0].text

        logger.debug("LLM API call successful")

        self._clean_response()

        logger.debug(f"System prompt: \n{system_prompt}")
        logger.debug(f"User prompt: \n{user_prompt}")
        logger.debug(f"LLM response: \n{self._raw_response}")

    def _create_ics_user_prompt(self, user_text, user_timezone_name):
        """
        [INTERFACE] Formats prompt template with user inputs
        [INPUTS] Event text, timezone
        [OUTPUTS] Formatted prompt string
        """  
        with open('event_creator/00_user_text_to_ics_v1.txt', 'r') as file:
            blank_user_prompt = file.read()

        utc_time = timezone.now().strftime('%Y-%m-%dT%H:%M') #NB: this is just to the minutes level of precision

        user_prompt = blank_user_prompt.format(
            utc_time,
            user_text,
            user_timezone_name if user_timezone_name is not None else "Not specified"
            )

        return user_prompt

    def _clean_response(self):
        """
        [INTERFACE] Parses XML response into structured event data
        [INPUTS] Raw XML in self._raw_response
        [OUTPUTS] Populated self.response dict with parsed fields (all strings)
        """
        
        def str_to_iso_dttm_str(date_str):
            """
            [INTERFACE] Safely parses datetime strings
            [OUTPUTS] ISO formatted string or None
            """            
            try:
                return datetime.fromisoformat(date_str).isoformat()
            except (ValueError, TypeError):
                return None

        def str_and_tz_to_dttm(date_str, timezone_name):
            """
            [INTERFACE] Safely parses datetime strings with timezone
            [OUTPUTS] datetime object or None
            """            
            try:
                return datetime.fromisoformat(date_str).replace(tzinfo=ZoneInfo(timezone_name))
            except (ValueError, TypeError, ZoneInfoNotFoundError):
                return None
            
        self.response = {
            "start_dttm_naive": None, # [DATA] ISO formatted string or None
            "end_dttm_naive": None, # [DATA] ISO formatted string or None
            "start_dttm_aware": None, # [DATA] datetime or None
            "end_dttm_aware": None, # [DATA] datetime or None
            "summary": None, # [DATA] string or None
            "description": None, # [DATA] string or None
            "location": None # [DATA] string or None
            }

        timezone_name = extract_first_xml(self._raw_response, "timezone_name")
        raw_start_date = extract_first_xml(self._raw_response, "dtstart")
        raw_end_date = extract_first_xml(self._raw_response, "dtend")
        
        self.response["start_dttm_naive"] = str_to_iso_dttm_str(raw_start_date)
        self.response["end_dttm_naive"] = str_to_iso_dttm_str(raw_end_date)
        
        self.response["start_dttm_aware"] = str_and_tz_to_dttm(raw_start_date, timezone_name)
        self.response["end_dttm_aware"] = str_and_tz_to_dttm(raw_end_date, timezone_name)

        self.response["summary"] = extract_first_xml(self._raw_response, "title")
        self.response["description"] = extract_first_xml(self._raw_response, "description")
        self.response["location"] = extract_first_xml(self._raw_response, "location")
    

# llm_caller = LlmCaller()
# import asyncio
# asyncio.run(llm_caller.text_to_ics("dmv appointment on the 23rd"))
# print(llm_caller.response)