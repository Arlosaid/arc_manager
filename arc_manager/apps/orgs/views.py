from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Organization
from .mixins import OrganizationAdminMixin
from .forms import OrganizationForm

class OrganizationDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de una organización"""
    model = Organization
    template_name = 'orgs/organization_detail.html'
    context_object_name = 'organization'
    
    def dispatch(self, request, *args, **kwargs):
        org = self.get_object()
        # Solo usuarios de la organización pueden verla
        if request.user.organization != org:
            messages.error(request, "No tienes permisos para ver esta organización.")
            return redirect('main:home')
        return super().dispatch(request, *args, **kwargs)

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
            return redirect('main:home')
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
        return redirect('main:home')
    
    return render(request, 'orgs/my_organization.html', {
        'organization': request.user.organization,
        'users': request.user.organization.users.all(),
        'admins': request.user.organization.get_admins(),
    })
