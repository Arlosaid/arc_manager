from django.urls import path
from . import views

app_name = 'orgs'

urlpatterns = [
    # Lista de organizaciones (solo superusuarios)
    path('', views.OrganizationListView.as_view(), name='list'),
    
    # Crear organización (solo superusuarios)
    path('crear/', views.OrganizationCreateView.as_view(), name='create'),
    
    # Ver detalles de organización
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='detail'),
    
    # Editar organización
    path('<int:pk>/editar/', views.OrganizationUpdateView.as_view(), name='edit'),
    
    # Mi organización (vista para usuarios normales)
    path('mi-organizacion/', views.my_organization, name='my_organization'),
] 