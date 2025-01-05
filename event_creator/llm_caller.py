from anthropic import AsyncAnthropic
import os
import re
from zoneinfo import ZoneInfo
from datetime import datetime

from django.utils import timezone

class LlmCaller:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.environ.get("PRODUCTION_ANTHROPIC_API_KEY"))
        self._raw_response = None
        self.response = {}

    async def text_to_ics(self, user_text, user_timezone_name=None):
        # call the llm
        # clean the response
        # validate the response

        with open('event_creator/00_system_text_to_ics_v1.txt', 'r') as file:
            system_prompt = file.read()

        user_prompt = self._create_ics_user_prompt(user_text, user_timezone_name)

        anthropic_response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            temperature=0.1,
            system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )

        self._raw_response = anthropic_response.content[0].text

        self._clean_response()

        print(system_prompt)
        print(user_prompt)
        print(self._raw_response)

    def _create_ics_user_prompt(self, user_text, user_timezone_name):
        # read the user prompt
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
        timezone_name = extract_first_xml(self._raw_response, "timezone_name")
        raw_start_date = extract_first_xml(self._raw_response, "dtstart")
        raw_end_date = extract_first_xml(self._raw_response, "dtend")
        
        if len(timezone_name) == 0:
            self.response["date_start"] = datetime.fromisoformat(raw_start_date)
            self.response["date_end"] = datetime.fromisoformat(raw_end_date)
        else:
            self.response["date_start"] = datetime.fromisoformat(raw_start_date).replace(tzinfo=ZoneInfo(timezone_name))
            self.response["date_end"] = datetime.fromisoformat(raw_end_date).replace(tzinfo=ZoneInfo(timezone_name))

        summary = extract_first_xml(self._raw_response, "title")
        self.response["summary"] = summary
        
        description = extract_first_xml(self._raw_response, "description")
        self.response["description"] = description

        location = extract_first_xml(self._raw_response, "location")
        self.response["location"] = location

def extract_first_xml(body_of_text, xml_tag):
    xml_tag_pattern = fr'<{xml_tag}>(.*?)</{xml_tag}>'
    matches = re.findall(xml_tag_pattern, body_of_text, re.DOTALL)

    #Get only the first match
    clean_xml_content = matches[0].strip()
    return clean_xml_content

# llm_caller = LlmCaller()
# import asyncio
# asyncio.run(llm_caller.text_to_ics("dmv appointment on the 23rd"))
# print(llm_caller.response)