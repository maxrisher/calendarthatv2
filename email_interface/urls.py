from django.urls import path
from .views import receive_email

urlpatterns = [
    path("email_event_creation_webhook/", receive_email, name="email_event_creation_webhook"),
]