from django.shortcuts import redirect, render
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'plans'

def plan_redirect_view(request):
    """
    Redirige a los usuarios a la página correcta según su rol.
    - Superusuarios: Al admin de Django.
    - Administradores de Org: Al dashboard de suscripción.
    - Otros usuarios autenticados: Al dashboard de suscripción.
    - No autenticados: A la página de login.
    """
    user = request.user
    if not user.is_authenticated:
        return redirect('accounts:login')
    
    if user.is_superuser:
        return redirect('/admin/plans/upgraderequest/')
    
    # Para MVP, todos los usuarios autenticados van al dashboard de su organización.
    return redirect('plans:subscription_dashboard')

urlpatterns = [
    path('', login_required(plan_redirect_view), name='index'),
    path('dashboard/', views.SubscriptionDashboardView.as_view(), name='subscription_dashboard'),
    path('request-upgrade/', views.RequestUpgradeView.as_view(), name='request_upgrade'),
]