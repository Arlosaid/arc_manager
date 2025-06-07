from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

from .forms import SimpleUserCreateForm, UserEditForm

User = get_user_model()
logger = logging.getLogger(__name__)

class UserListView(LoginRequiredMixin, ListView):
    """Vista para listar usuarios"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 15
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.select_related('organization')
        
        # Solo los org_admin pueden ver usuarios de su organización
        if user.is_org_admin and user.organization:
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

class SimpleUserCreateView(LoginRequiredMixin, View):
    """Vista para crear usuarios de forma simple"""
    template_name = 'users/simple_create_user.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Solo org_admin pueden crear usuarios
        if not request.user.is_org_admin:
            raise PermissionDenied("No tienes permisos para crear usuarios")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = SimpleUserCreateForm(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = SimpleUserCreateForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                user, temp_password, email_sent = form.save(request)
                
                if email_sent:
                    messages.success(
                        request,
                        f'Usuario {user.username or user.email} creado exitosamente. '
                        f'Se han enviado las credenciales por correo electrónico.'
                    )
                else:
                    messages.warning(
                        request,
                        f'Usuario {user.username or user.email} creado exitosamente, '
                        f'pero no se pudo enviar el correo electrónico. '
                        f'Credenciales: {user.email} / {temp_password}'
                    )
                
                return redirect('users:user_list')
                
            except Exception as e:
                logger.error(f"Error al crear usuario: {str(e)}")
                messages.error(request, f"Error al crear el usuario: {str(e)}")
        
        return render(request, self.template_name, {'form': form})

class UserEditView(LoginRequiredMixin, View):
    """Vista para editar usuarios"""
    template_name = 'users/user_edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        user_to_edit = get_object_or_404(User, pk=kwargs['pk'])
        current_user = request.user
        
        # Verificar permisos - solo org_admin de la misma organización o el propio usuario
        if current_user.is_org_admin and current_user.organization:
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
            form.save()
            messages.success(request, f"Usuario {user_to_edit.username or user_to_edit.email} actualizado exitosamente.")
            return redirect('users:user_list')
        
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
        
        # Verificar permisos - solo org_admin de la misma organización o el propio usuario
        if current_user.is_org_admin and current_user.organization:
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

class UserDeleteView(LoginRequiredMixin, View):
    """Vista para eliminar usuarios"""
    template_name = 'users/user_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        user_to_delete = get_object_or_404(User, pk=kwargs['pk'])
        current_user = request.user
        
        # Solo org_admin puede eliminar usuarios de su organización
        if not (current_user.is_org_admin and current_user.organization and 
                user_to_delete.organization == current_user.organization):
            raise PermissionDenied("No tienes permisos para eliminar este usuario")
        
        # No se puede eliminar a si mismo
        if user_to_delete == current_user:
            raise PermissionDenied("No puedes eliminarte a ti mismo")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        user_to_delete = get_object_or_404(User, pk=pk)
        return render(request, self.template_name, {'user_to_delete': user_to_delete})
    
    def post(self, request, pk):
        user_to_delete = get_object_or_404(User, pk=pk)
        
        try:
            username = user_to_delete.username or user_to_delete.email
            user_to_delete.delete()
            messages.success(request, f"Usuario {username} eliminado exitosamente.")
        except Exception as e:
            logger.error(f"Error al eliminar usuario: {str(e)}")
            messages.error(request, f"Error al eliminar el usuario: {str(e)}")
        
        return redirect('users:user_list')
