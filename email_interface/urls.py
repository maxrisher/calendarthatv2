from django.urls import path
from .views import receive_email

urlpatterns = [
    path("create_event/", receive_email, name="create_event_email"),
]