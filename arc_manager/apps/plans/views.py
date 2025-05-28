from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .models import Plan
from apps.orgs.models import Organization

class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere que el usuario sea superusuario"""
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para acceder a esta sección.")
        return redirect('main:home')

class OrgAdminRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere que el usuario sea admin de una organización"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return (self.request.user.is_superuser or 
                hasattr(self.request.user, 'organization') and 
                self.request.user.is_org_admin)
    
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para acceder a esta sección.")
        return redirect('main:home')

# ===================== VISTAS PARA SUPERUSUARIOS =====================

class SuperuserPlanListView(SuperuserRequiredMixin, ListView):
    """Vista para que los superusuarios gestionen todos los planes del sistema"""
    model = Plan
    template_name = 'plans/superuser/plan_list.html'
    context_object_name = 'plans'
    
    def get_queryset(self):
        return Plan.objects.all().order_by('price', 'max_users')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_plans'] = Plan.objects.count()
        context['active_plans'] = Plan.objects.filter(is_active=True).count()
        context['organizations_count'] = Organization.objects.count()
        return context

class SuperuserPlanCreateView(SuperuserRequiredMixin, CreateView):
    """Vista para crear nuevos planes (solo superusuarios)"""
    model = Plan
    template_name = 'plans/superuser/plan_form.html'
    fields = ['name', 'display_name', 'description', 'max_users', 'price', 'is_active']
    success_url = reverse_lazy('plans:superuser_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Plan '{self.object.display_name}' creado exitosamente."
        )
        return response

class SuperuserPlanUpdateView(SuperuserRequiredMixin, UpdateView):
    """Vista para editar planes existentes (solo superusuarios)"""
    model = Plan
    template_name = 'plans/superuser/plan_form.html'
    fields = ['name', 'display_name', 'description', 'max_users', 'price', 'is_active']
    success_url = reverse_lazy('plans:superuser_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Plan '{self.object.display_name}' actualizado exitosamente."
        )
        return response

class SuperuserPlanDeleteView(SuperuserRequiredMixin, DeleteView):
    """Vista para eliminar planes (solo superusuarios)"""
    model = Plan
    template_name = 'plans/superuser/plan_confirm_delete.html'
    success_url = reverse_lazy('plans:superuser_list')
    
    def delete(self, request, *args, **kwargs):
        plan = self.get_object()
        
        # Verificar que no haya organizaciones usando este plan
        orgs_using_plan = Organization.objects.filter(plan=plan).count()
        if orgs_using_plan > 0:
            messages.error(
                request, 
                f"No se puede eliminar el plan '{plan.display_name}' porque {orgs_using_plan} "
                f"organización{'es' if orgs_using_plan > 1 else ''} lo está{'n' if orgs_using_plan > 1 else ''} usando."
            )
            return redirect('plans:superuser_list')
        
        messages.success(
            request, 
            f"Plan '{plan.display_name}' eliminado exitosamente."
        )
        return super().delete(request, *args, **kwargs)

# ===================== VISTAS PARA ADMIN DE ORGANIZACIÓN =====================

class OrgPlanManagementView(OrgAdminRequiredMixin, ListView):
    """Vista para que los admins de org gestionen el plan de su organización"""
    model = Plan
    template_name = 'plans/org_admin/plan_management.html'
    context_object_name = 'available_plans'
    
    def get_queryset(self):
        return Plan.objects.filter(is_active=True).order_by('price', 'max_users')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_superuser:
            # Si es superusuario, puede gestionar cualquier organización
            org_id = self.request.GET.get('org_id')
            if org_id:
                organization = get_object_or_404(Organization, id=org_id)
            else:
                organization = Organization.objects.first()
        else:
            # Si es admin de org, solo puede gestionar su organización
            organization = user.organization
        
        context['organization'] = organization
        context['current_plan'] = organization.plan if organization else None
        context['user_stats'] = organization.can_add_user_detailed() if organization else None
        context['is_superuser'] = user.is_superuser
        
        if user.is_superuser:
            context['all_organizations'] = Organization.objects.all().order_by('name')
        
        return context

@login_required
def change_organization_plan(request):
    """Vista AJAX para cambiar el plan de una organización"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    user = request.user
    org_id = request.POST.get('org_id')
    plan_id = request.POST.get('plan_id')
    
    try:
        # Verificar permisos
        if user.is_superuser:
            organization = get_object_or_404(Organization, id=org_id)
        elif hasattr(user, 'organization') and user.is_org_admin:
            organization = user.organization
            if str(organization.id) != str(org_id):
                raise PermissionDenied("No puedes cambiar el plan de otra organización")
        else:
            raise PermissionDenied("No tienes permisos para cambiar planes")
        
        new_plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        
        # Verificar que el nuevo plan permita los usuarios actuales
        current_user_count = organization.get_user_count()
        if current_user_count > new_plan.max_users:
            return JsonResponse({
                'success': False, 
                'error': f'No puedes cambiar a este plan porque tu organización tiene {current_user_count} usuarios '
                        f'y el plan seleccionado solo permite {new_plan.max_users}. '
                        f'Reduce el número de usuarios primero.'
            })
        
        # Realizar el cambio
        with transaction.atomic():
            old_plan_name = organization.plan.display_name if organization.plan else "Sin plan"
            organization.plan = new_plan
            organization.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Plan cambiado exitosamente de "{old_plan_name}" a "{new_plan.display_name}"',
            'new_plan': {
                'name': new_plan.display_name,
                'max_users': new_plan.max_users,
                'price': str(new_plan.price)
            }
        })
        
    except PermissionDenied as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Error interno del servidor'})

# ===================== VISTAS PÚBLICAS/INFORMATIVAS =====================

@login_required
def plan_pricing(request):
    """Vista de gestión de planes - solo para superusuarios y admins de org"""
    user = request.user
    
    # Verificar permisos - solo superusuarios y admins de org
    if not (user.is_superuser or (hasattr(user, 'organization') and user.is_org_admin)):
        messages.error(request, "No tienes permisos para acceder a la gestión de planes.")
        return redirect('main:home')
    
    # Redirigir según el tipo de usuario
    if user.is_superuser:
        return redirect('plans:superuser_list')
    else:
        return redirect('plans:org_management')
