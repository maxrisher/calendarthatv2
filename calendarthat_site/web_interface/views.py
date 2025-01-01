from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'web_interface/home.html')

async def create_event_web(request):
    # test if the user is authenticated; get their details if so

    # create a new event request in the database

    # create and start running an async task to process the request, passing our request id

    # return the task ID to the user

def get_event_status(request):
    # Check on the status of the event

def download_calendar_event(request):
    # Download the calendar event