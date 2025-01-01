
#CalEvent
#__init__ requires an event id
# init tries to read in any existing data in the database about the event

# Requires text
# optional user timezone

# stores event start time
# stores event end time
# stores event location

# async formalize_event() method uses a prompt to call an LLM and create a calendar event. 
# 0. First checks to see that its event data has not already been set.
# 1. Send claude 3.5 a prompt with the user text and user timezone
# 2. Extract and set all event properties on its self
# 3. Write event properties to the database object

# to_ical() creates an ical file

# to_gcal_link creates a gcal link

# to_outlook_link creates an outlook link