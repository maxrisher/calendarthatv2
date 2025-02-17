import pytz

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser

TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]

class CustomUserCreationForm(UserCreationForm):
    time_zone_name = forms.ChoiceField(
        choices=TIMEZONE_CHOICES,
        required=True,
        widget=forms.Select(attr={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ("email", "time_zone_name")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")