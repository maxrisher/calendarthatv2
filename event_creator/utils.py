import re

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
