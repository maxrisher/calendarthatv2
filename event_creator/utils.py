import re
from ics import Calendar, Event as ICSEvent
from datetime import datetime

def extract_first_xml(body_of_text, xml_tag):
    xml_tag_pattern = fr'<{xml_tag}>(.*?)</{xml_tag}>'
    matches = re.findall(xml_tag_pattern, body_of_text, re.DOTALL)

    #Get only the first match
    clean_xml_content = matches[0].strip()
    return clean_xml_content

def extract_first_xml(body_of_text, xml_tag):
    """
    Input: body of text (the text to search within), xml_tag (the name of the tag to search for)
    Output: the text within the first pair of xml tags found or None
    """
    xml_tag_pattern = fr'<{xml_tag}>(.*?)</{xml_tag}>'
    matches = re.findall(xml_tag_pattern, body_of_text, re.DOTALL)

    #Get only the first match
    return matches[0].strip() if matches else None

def raise_if_invalid_ics(name, begin, end, description, location):
    if not name:
        raise ValueError("Event must have a summary/title")
    if not begin:
        raise ValueError("Event must have a start time")
    if not end:
        raise ValueError("Event must have an end time")
    
    cal = Calendar()
    event = ICSEvent(
        name=name,
        begin=begin,
        end=end,
        description=description,
        location=location
    )
    if event.end <= event.begin:
        raise ValueError("End time must be after start time")
    
    cal.events.add(event)
    
    # Try to serialize - this will raise if invalid
    cal.serialize()

def iso_8601_str_rewrite(iso_8601_str, format):
    naive_dttm = datetime.fromisoformat(iso_8601_str)

    if format == "outlook":
        return naive_dttm.strftime("%Y-%m-%dT%H:%M:%S")
    if format == "gcal" or format == "ics":
        return naive_dttm.strftime("%Y%m%dT%H%M%S")
    else:
        return naive_dttm.strftime("%Y%m%dT%H%M%S")