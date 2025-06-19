from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from django.conf import settings

from .forms import SimpleUserCreateForm, SimpleUserEditForm

User = get_user_model()
logger = logging.getLogger(__name__)

class UserListView(LoginRequiredMixin, ListView):
    """Vista para listar usuarios - Solo para org_admin"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 15
    
    def get_queryset(self):
        user = self.request.user
        
        # Solo los org_admin pueden ver usuarios
        if not user.is_org_admin or not user.organization:
            raise PermissionDenied("No tienes permisos para ver usuarios")
        
        # Admin de org solo ve usuarios de su organización (excluyendo superusers)
        queryset = User.objects.filter(
            organization=user.organization,
            is_superuser=False  # Excluir superusers de la vista
        ).select_related('organization')
        
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
        user = self.request.user
        
        # Calcular solo las métricas esenciales basadas en la organización del usuario
        org_users = User.objects.filter(
            organization=user.organization,
            is_superuser=False  # Excluir superusers para consistencia
        )
        
        # Métricas mejoradas
        total_users = org_users.count()
        active_users = org_users.filter(is_active=True).count()
        inactive_users = total_users - active_users
        percentage_active = round((active_users / total_users * 100) if total_users > 0 else 0)
        
        # Obtener límites de la organización
        max_users = user.organization.get_max_users() if user.organization else 0
        remaining_slots = max(0, max_users - total_users) if max_users > 0 else 0
        
        context['total_users'] = total_users
        context['active_users'] = active_users
        context['inactive_users'] = inactive_users
        context['percentage_active'] = percentage_active
        context['max_users'] = max_users
        context['remaining_slots'] = remaining_slots
        
        # Pasar búsqueda al contexto
        context['search'] = self.request.GET.get('search', '')
        
        return context

class SimpleUserCreateView(LoginRequiredMixin, View):
    """Vista para crear usuarios - Solo para org_admin"""
    template_name = 'users/simple_create_user.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Solo org_admin pueden crear usuarios
        if not request.user.is_org_admin:
            logger.warning(f"Acceso denegado para crear usuario: {request.user.email}")
            raise PermissionDenied("No tienes permisos para crear usuarios")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = SimpleUserCreateForm(user=request.user)
        
        # Log solo si hay problemas con límites de organización
        if request.user.organization:
            limit_info = request.user.organization.can_add_user_detailed()
            if not limit_info['can_add']:
                logger.warning(f"Límite de usuarios alcanzado para {request.user.organization.name}: {limit_info['total_users']}/{limit_info['max_users']}")
        
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = SimpleUserCreateForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                user, temp_password, email_sent = form.save(request)
                
                # Log solo el resultado importante
                logger.info(f"Usuario creado: {user.email} por {request.user.email}")
                
                if email_sent:
                    messages.success(
                        request,
                        f'Usuario {user.username or user.email} creado exitosamente. '
                        f'Se han enviado las credenciales por correo electrónico.'
                    )
                else:
                    # Siempre mostrar mensaje amigable, errores técnicos solo en logs
                    messages.warning(
                        request,
                        f'Usuario {user.username or user.email} creado exitosamente, '
                        f'pero no se pudo enviar el correo electrónico. '
                        f'Por favor, proporciona las credenciales manualmente: {user.email}'
                    )
                    
                    # Log detallado para desarrolladores (incluir contraseña temporal)
                    logger.warning(f"Error enviando email a usuario creado: {user.email} - Contraseña temporal: {temp_password}")
                
                return redirect('users:user_list')
                
            except Exception as e:
                # Log detallado del error para desarrolladores
                logger.error(f"Error al crear usuario: {str(e)}", exc_info=True)
                
                # Siempre mostrar mensaje amigable, nunca errores técnicos
                messages.error(request, "Ha ocurrido un error al crear el usuario. Por favor, contacta con soporte técnico.")
                    
        else:
            # Log solo errores críticos
            if form.non_field_errors():
                logger.warning(f"Errores de validación al crear usuario: {form.non_field_errors()}")
        
        return render(request, self.template_name, {'form': form})
    


class UserEditView(LoginRequiredMixin, View):
    """Vista para editar usuarios"""
    template_name = 'users/user_edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        user_to_edit = get_object_or_404(User, pk=kwargs['pk'])
        current_user = request.user
        
        # Excluir superusers de la edición
        if user_to_edit.is_superuser:
            raise PermissionDenied("Los superusuarios solo se gestionan desde el admin")
        
        # Verificar permisos
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
        form = SimpleUserEditForm(instance=user_to_edit, user=request.user)
        return render(request, self.template_name, {
            'form': form, 
            'user_to_edit': user_to_edit
        })
    
    def post(self, request, pk):
        user_to_edit = get_object_or_404(User, pk=pk)
        form = SimpleUserEditForm(request.POST, instance=user_to_edit, user=request.user)
        
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
        
        # Excluir superusers de la vista
        if user_to_view.is_superuser:
            raise PermissionDenied("Los superusuarios solo se gestionan desde el admin")
        
        # Verificar permisos
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



class UserDeleteAjaxView(LoginRequiredMixin, View):
    """Vista AJAX para obtener información del usuario a eliminar"""
    
    def dispatch(self, request, *args, **kwargs):
        user_to_delete = get_object_or_404(User, pk=kwargs['pk'])
        current_user = request.user
        
        # Excluir superusers de la eliminación
        if user_to_delete.is_superuser:
            raise PermissionDenied("Los superusuarios solo se gestionan desde el admin")
        
        # Solo org_admin puede eliminar usuarios de su organización
        if not (current_user.is_org_admin and current_user.organization and 
                user_to_delete.organization == current_user.organization):
            raise PermissionDenied("No tienes permisos para eliminar este usuario")
        
        # No se puede eliminar a si mismo
        if user_to_delete == current_user:
            raise PermissionDenied("No puedes eliminarte a ti mismo")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        """Obtener información del usuario para mostrar en el modal"""
        user_to_delete = get_object_or_404(User, pk=pk)
        
        user_data = {
            'id': user_to_delete.id,
            'first_name': user_to_delete.first_name,
            'last_name': user_to_delete.last_name,
            'username': user_to_delete.username,
            'email': user_to_delete.email,
            'is_active': user_to_delete.is_active,
            'is_org_admin': user_to_delete.is_org_admin,
            'organization': user_to_delete.organization.name if user_to_delete.organization else 'Sin organización',
            'initials': f"{user_to_delete.first_name[:1]}{user_to_delete.last_name[:1]}".upper(),
            'full_name': f"{user_to_delete.first_name} {user_to_delete.last_name}",
        }
        
        return JsonResponse({
            'success': True,
            'user': user_data
        })
    
    def post(self, request, pk):
        """Procesar la eliminación del usuario"""
        user_to_delete = get_object_or_404(User, pk=pk)
        
        try:
            # Verificar que se confirmó la eliminación
            confirm_delete = request.POST.get('confirm_delete')
            if confirm_delete != 'yes':
                return JsonResponse({
                    'success': False,
                    'error': 'Confirmación requerida'
                })
            
            username = user_to_delete.username or user_to_delete.email
            full_name = f"{user_to_delete.first_name} {user_to_delete.last_name}"
            
            # Log importante para auditoría
            logger.info(f"Usuario eliminado: {user_to_delete.email} por {request.user.email}")
            
            user_to_delete.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario {full_name} ({username}) eliminado exitosamente.'
            })
            
        except Exception as e:
            # Log detallado del error para desarrolladores
            logger.error(f"Error al eliminar usuario: {str(e)}")
            
            # Siempre respuesta amigable, nunca errores técnicos
            return JsonResponse({
                'success': False,
                'error': 'Error al eliminar el usuario. Por favor, contacta con soporte técnico.'
            }, status=500)
