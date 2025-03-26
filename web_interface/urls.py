from django.urls import path

from . import views, views_single_event_creation

urlpatterns = [
    path('', views_single_event_creation.home, name='home'),
    path('create/', views_single_event_creation.create_event_web, name='create_event_web'),
    path('event_status/', views_single_event_creation.get_event_status, name='get_event_status'),
    path('download/', views_single_event_creation.download_calendar_event, name='download_calendar_event'),
    path('check_auth/', views_single_event_creation.check_auth, name='check_auth'),
    path('extension_create/', views_single_event_creation.create_event_browser_extension, name='create_event_browser_extension'),
    
    path('create_multiple/', views.create_events_web, name='create_multiple_events_web'),
    path('event_builder_status/', views.get_event_builder_status, name='get_event_builder_status'),
    path('download_multiple_events/', views.download_multiple_events, name='download_multiple_events'),
]