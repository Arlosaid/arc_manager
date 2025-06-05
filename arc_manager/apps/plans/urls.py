from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    # URLs públicas
    path('pricing/', views.PublicPricingView.as_view(), name='pricing'),
    
    # URLs para usuarios autenticados
    path('dashboard/', views.SubscriptionDashboardView.as_view(), name='subscription_dashboard'),
    path('upgrade/', views.UpgradePlanView.as_view(), name='upgrade_plan'),
    
    # URLs para Superusuarios - Gestión de Planes
    path('admin/', views.SuperuserPlanListView.as_view(), name='superuser_list'),
    path('admin/create/', views.SuperuserPlanCreateView.as_view(), name='superuser_create'),
    path('admin/<int:pk>/edit/', views.SuperuserPlanUpdateView.as_view(), name='superuser_edit'),
    path('admin/<int:pk>/delete/', views.SuperuserPlanDeleteView.as_view(), name='superuser_delete'),
    
    # URLs para Superusuarios - Gestión Manual de Suscripciones (MVP)
    path('admin/subscriptions/', views.SuperuserSubscriptionManagementView.as_view(), name='superuser_subscription_management'),
    path('admin/payments/manual/', views.ManualPaymentProcessView.as_view(), name='manual_payment'),
    
    # URLs para Admin de Organización
    path('manage/', views.OrgPlanManagementView.as_view(), name='org_management'),
    path('change-plan/', views.change_organization_plan, name='change_plan'),
    
    # URLs para Staff (procesamiento manual de pagos)
    path('payments/', views.ProcessPaymentView.as_view(), name='process_payment'),
    
    # API endpoints para el futuro
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
    
    if user.is_superuser:
        return redirect('plans:superuser_subscription_management')  # Cambiado para ir directo a gestión de suscripciones
    elif user.is_org_admin or user.organization:
        return redirect('plans:subscription_dashboard')
    else:
        return redirect('plans:pricing')