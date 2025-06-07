from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Organization
from .mixins import OrganizationAdminMixin
from .forms import OrganizationForm

class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar organizaciones"""
    model = Organization
    form_class = OrganizationForm
    template_name = 'orgs/organization_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        org = self.get_object()
        # Solo admins de la organización pueden editarla
        if not (request.user.organization == org and request.user.is_org_admin):
            messages.error(request, "No tienes permisos para editar esta organización.")
            return redirect('main:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('orgs:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        old_plan = None
        old_max_users = None
        
        # Capturar información del plan anterior si existe la instancia
        if hasattr(self, 'object') and self.object.pk:
            old_plan = self.object.plan
            old_max_users = self.object.get_max_users()
        
        response = super().form_valid(form)
        
        new_plan = self.object.plan
        new_max_users = self.object.get_max_users()
        
        # Mensaje personalizado dependiendo de si cambió el plan
        if old_plan and old_plan != new_plan:
            messages.success(
                self.request, 
                f"Organización '{self.object.name}' actualizada. "
                f"Plan cambiado de '{old_plan.display_name}' a '{new_plan.display_name}'. "
                f"Nuevo límite de usuarios: {new_max_users}."
            )
        else:
            messages.success(
                self.request, 
                f"Organización '{self.object.name}' actualizada exitosamente. "
                f"Plan actual: {new_plan.display_name if new_plan else 'Sin plan'} "
                f"({new_max_users} usuario{'s' if new_max_users != 1 else ''} máximo)."
            )
        
        return response

@login_required
def my_organization(request):
    """Vista para que el usuario vea su propia organización"""
    if not request.user.organization:
        messages.info(request, "No estás asignado a ninguna organización.")
        return redirect('main:dashboard')
    
    return render(request, 'orgs/my_organization.html', {
        'organization': request.user.organization,
        'users': request.user.organization.users.all(),
        'admins': request.user.organization.get_admins(),
        # Puedes agregar aquí active_users si lo necesitas
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
