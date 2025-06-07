from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    # URLs públicas
    path('pricing/', views.PublicPricingView.as_view(), name='pricing'),
    
    # URLs para usuarios autenticados
    path('dashboard/', views.SubscriptionDashboardView.as_view(), name='subscription_dashboard'),
    
    # URLs para sistema de upgrade (solo para usuarios)
    path('request-upgrade/', views.RequestUpgradeView.as_view(), name='request_upgrade'),
    
    # URLs para Staff (procesamiento manual de pagos)
    path('payments/', views.ProcessPaymentView.as_view(), name='process_payment'),
    
    # API endpoints
    path('api/check-limits/', views.check_subscription_limits, name='check_limits'),
    
    # Redirección por defecto basada en permisos del usuario
    path('', views.plan_pricing_redirect, name='list'),
]

# Función de redirección inteligente
def plan_pricing_redirect(request):
    """Redirige según el tipo de usuario"""
    user = request.user
    
    if not user.is_authenticated:
        return redirect('plans:pricing')
    
    # Los superusers son redirigidos al admin de Django - toda la gestión se hace ahí
    if user.is_superuser:
        return redirect('/admin/plans/upgraderequest/')
    elif user.is_org_admin:
        return redirect('plans:subscription_dashboard')
    else:
        return redirect('plans:pricing')