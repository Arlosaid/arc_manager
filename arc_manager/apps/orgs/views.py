from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Organization
from .mixins import OrganizationAdminMixin
from .forms import OrganizationForm

# =============================================================================
# NOTA IMPORTANTE: Vista de edición de organizaciones DESHABILITADA
# =============================================================================
# 
# PROBLEMA: Permitir que un org_admin edite su organización puede causar:
# 
# 1. CAMBIO DE NOMBRE:
#    - Afecta logs del sistema, emails automáticos, reportes
#    - Rompe referencias en URLs del admin
#    - Confunde a usuarios y administradores del sistema
# 
# 2. DESACTIVAR ORGANIZACIÓN (is_active=False):
#    - Bloquea acceso a TODOS los usuarios incluido el propio admin
#    - Rompe funcionalidades del middleware de validación
#    - Crea problemas con suscripciones y facturación
#    - El admin no puede volver a activarla después
# 
# 3. BAJO VALOR DE LA FUNCIONALIDAD:
#    - Solo quedaría editar la descripción
#    - No justifica toda una vista compleja
# 
# SOLUCIÓN: Solo superusers pueden editar organizaciones desde el admin panel
# 
# =============================================================================

# class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
#     """
#     Vista DESHABILITADA para editar organizaciones.
#     """
#     pass

@login_required
def my_organization(request):
    """Vista para que el usuario vea su propia organización"""
    if not request.user.organization:
        # NO mostrar mensaje aquí - esto debería manejarse a nivel de middleware
        # o en la página principal donde es más apropiado
        return redirect('main:dashboard')
    
    organization = request.user.organization
    
    return render(request, 'orgs/my_organization.html', {
        'organization': organization,
        'users': organization.users.all(),
        'admins': organization.get_admins(),
        'active_users': organization.users.filter(is_active=True),
    })

class OrganizationDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver los detalles de una organización"""
    model = Organization
    template_name = 'orgs/my_organization.html'
    context_object_name = 'organization'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.get_object()
        
        # Obtener usuarios de la organización
        context['users'] = organization.users.all()
        context['admins'] = organization.users.filter(is_org_admin=True)
        context['active_users'] = organization.users.filter(is_active=True)
        
        # Calcular porcentaje de capacidad usando get_max_users()
        max_users = organization.get_max_users()
        context['percentage'] = int((organization.get_user_count() / max_users) * 100) if max_users > 0 else 0
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        org = self.get_object()
        # Solo usuarios de la organización pueden verla
        if not (request.user.organization == org):
            messages.error(request, "No tienes permisos para ver esta organización.")
            return redirect('main:dashboard')
        return super().dispatch(request, *args, **kwargs)
