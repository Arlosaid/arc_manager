from django.urls import path
from . import views

app_name = 'orgs'

urlpatterns = [
    # Ver detalles de una organización específica
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='detail'),
    
    # Editar organización - DESHABILITADO
    # RAZÓN: Los org_admin no deberían poder editar campos críticos como:
    # - Nombre (afecta logs, emails, reportes)
    # - Estado activo (puede bloquear a todos los usuarios)
    # Solo superusers pueden hacer estos cambios desde el admin panel
    # path('<int:pk>/editar/', views.OrganizationUpdateView.as_view(), name='edit'),

    # Mi organización (vista para usuarios normales)
    path('mi-organizacion/', views.my_organization, name='my_organization'),
] 