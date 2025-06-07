from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    """Vista del dashboard principal"""
    context = {
        'organization': request.user.organization,
        'recent_activities': []  # TODO: Implementar obtención de actividades recientes
    }
    return render(request, 'dashboard.html', context)