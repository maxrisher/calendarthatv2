from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from asgiref.sync import sync_to_async

from .forms import UserSettingsForm

@login_required
async def user_settings(request):
    user = await request.auser()
    
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=user)
        if form.is_valid():
            await sync_to_async(form.save)()
            return redirect(reverse('user_settings')) # check this
        
    else:
        form = UserSettingsForm(instance=user)
        
    return render(request, 'account/settings.html', {'user': user, 'form': form})
        