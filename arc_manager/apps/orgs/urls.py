from django.urls import path
from . import views

app_name = 'orgs'

urlpatterns = [
    # Ver detalles de organización
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='detail'),
    
    # Editar organización
    path('<int:pk>/editar/', views.OrganizationUpdateView.as_view(), name='edit'),
    
    # Mi organización (vista para usuarios normales)
    path('mi-organizacion/', views.my_organization, name='my_organization'),
] 