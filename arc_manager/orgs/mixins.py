from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Organization

class OrganizationMixin:
    """
    Mixin para vistas que necesitan filtrar por organización del usuario
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'organization') and self.request.user.organization:
            # Si el modelo tiene un campo 'organization', filtrar por él
            if hasattr(queryset.model, 'organization'):
                return queryset.filter(organization=self.request.user.organization)
        return queryset
    
    def form_valid(self, form):
        # Asignar automáticamente la organización al crear objetos
        if hasattr(form.instance, 'organization') and self.request.user.organization:
            form.instance.organization = self.request.user.organization
        return super().form_valid(form)

class OrganizationRequiredMixin:
    """
    Mixin que requiere que el usuario tenga una organización asignada
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        if not request.user.organization and not request.user.is_superuser:
            raise PermissionDenied("Necesitas estar asignado a una organización para acceder a esta página.")
        
        return super().dispatch(request, *args, **kwargs)

class OrganizationAdminMixin:
    """
    Mixin que requiere permisos de administrador de organización
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        if not request.user.can_manage_organization():
            raise PermissionDenied("No tienes permisos para administrar esta organización.")
        
        return super().dispatch(request, *args, **kwargs) 