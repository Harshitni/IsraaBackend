from django.shortcuts import render
from .forms import DuaaForm

def create_duaa(request):
    form = DuaaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return render(request, 'duaas/success.html')
    return render(request, 'duaas/create_duaa.html', {'form': form})
