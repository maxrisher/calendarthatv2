from zoneinfo import available_timezones

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from allauth.account.forms import SignupForm

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")
        
class CustomSignupForm(SignupForm):
    TIMEZONES = (sorted(list(available_timezones())))
    
    time_zone_name = forms.ChoiceField(
        choices = [(tz, tz) for tz in TIMEZONES],
        label = "Time Zone",
        required = True
    )
    
    def save(self, request):
        user = super().save(request)
        user.time_zone_name = self.cleaned_data['time_zone_name']
        user.save()
        return user
    
class UserSettingsForm(forms.ModelForm):
    TIMEZONES = sorted(list(available_timezones()))
    time_zone_name = forms.ChoiceField(
        choices = [(tz, tz) for tz in TIMEZONES]
    )
    
    class Meta:
        model = CustomUser
        fields = ['time_zone_name']