from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_event_web, name='create_event_web'),
    path('event_status/', views.get_event_status, name='get_event_status'),
    path('download/', views.download_calendar_event, name='download_calendar_event'),
    path('check_auth/', views.check_auth, name='check_auth'),
    path('extension_create/', views.create_event_browser_extension, name='create_event_browser_extension'),
]