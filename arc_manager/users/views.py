from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Q

from .forms import SimpleUserCreateForm, UserEditForm

User = get_user_model()

class UserListView(LoginRequiredMixin, ListView):
    """Vista para listar usuarios"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 15
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.select_related('organization')
        
        # Filtrar según permisos
        if user.is_superuser:
            # Superuser ve todos los usuarios
            queryset = queryset.all()
        elif user.is_org_admin and user.organization:
            # Admin de org solo ve usuarios de su organización
            queryset = queryset.filter(organization=user.organization)
        else:
            # Usuarios normales no pueden ver otros usuarios
            raise PermissionDenied("No tienes permisos para ver usuarios")
        
        # Filtro de búsqueda
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class SimpleCreateUserView(LoginRequiredMixin, View):
    """Vista simple para crear usuarios individuales"""
    template_name = 'users/simple_create_user.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_org_admin):
            raise PermissionDenied("No tienes permisos para crear usuarios")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = SimpleUserCreateForm(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = SimpleUserCreateForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                user = form.save()
                messages.success(
                    request, 
                    f"Usuario '{user.username}' ({user.first_name} {user.last_name}) creado exitosamente"
                )
                return redirect('users:list')  # Ir a la lista de usuarios
                
            except Exception as e:
                messages.error(request, f"Error al crear el usuario: {str(e)}")
        
        return render(request, self.template_name, {'form': form})

class UserEditView(LoginRequiredMixin, View):
    """Vista para editar usuarios"""
    template_name = 'users/user_edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        user_to_edit = get_object_or_404(User, pk=kwargs['pk'])
        current_user = request.user
        
        # Verificar permisos
        if current_user.is_superuser:
            # Superuser puede editar cualquier usuario
            pass
        elif current_user.is_org_admin and current_user.organization:
            # Admin de org solo puede editar usuarios de su organización
            if user_to_edit.organization != current_user.organization:
                raise PermissionDenied("No tienes permisos para editar este usuario")
        else:
            # Solo pueden editar su propio perfil
            if user_to_edit != current_user:
                raise PermissionDenied("No tienes permisos para editar este usuario")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        user_to_edit = get_object_or_404(User, pk=pk)
        form = UserEditForm(instance=user_to_edit, user=request.user)
        return render(request, self.template_name, {
            'form': form, 
            'user_to_edit': user_to_edit
        })
    
    def post(self, request, pk):
        user_to_edit = get_object_or_404(User, pk=pk)
        form = UserEditForm(request.POST, instance=user_to_edit, user=request.user)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, 
                    f"Usuario '{user_to_edit.username}' actualizado exitosamente"
                )
                return redirect('users:list')
                
            except Exception as e:
                messages.error(request, f"Error al actualizar el usuario: {str(e)}")
        
        return render(request, self.template_name, {
            'form': form, 
            'user_to_edit': user_to_edit
        })

class UserDetailView(LoginRequiredMixin, View):
    """Vista para ver detalles de un usuario"""
    template_name = 'users/user_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        user_to_view = get_object_or_404(User, pk=kwargs['pk'])
        current_user = request.user
        
        # Verificar permisos
        if current_user.is_superuser:
            # Superuser puede ver cualquier usuario
            pass
        elif current_user.is_org_admin and current_user.organization:
            # Admin de org solo puede ver usuarios de su organización
            if user_to_view.organization != current_user.organization:
                raise PermissionDenied("No tienes permisos para ver este usuario")
        else:
            # Solo pueden ver su propio perfil
            if user_to_view != current_user:
                raise PermissionDenied("No tienes permisos para ver este usuario")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        user_to_view = get_object_or_404(User, pk=pk)
        return render(request, self.template_name, {'user_to_view': user_to_view})
