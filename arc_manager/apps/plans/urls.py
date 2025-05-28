from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    # Vistas públicas/informativas
    path('pricing/', views.plan_pricing, name='pricing'),
    
    # Vistas para Superusuarios
    path('admin/', views.SuperuserPlanListView.as_view(), name='superuser_list'),
    path('admin/create/', views.SuperuserPlanCreateView.as_view(), name='superuser_create'),
    path('admin/<int:pk>/edit/', views.SuperuserPlanUpdateView.as_view(), name='superuser_edit'),
    path('admin/<int:pk>/delete/', views.SuperuserPlanDeleteView.as_view(), name='superuser_delete'),
    
    # Vistas para Admin de Organización
    path('manage/', views.OrgPlanManagementView.as_view(), name='org_management'),
    path('change-plan/', views.change_organization_plan, name='change_plan'),
    
    # Redirección por defecto
    path('', views.plan_pricing, name='list'),
] 