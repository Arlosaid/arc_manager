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

from .forms_simplified import SimpleUserCreateForm, SimpleUserEditForm

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
        
        context['total_users'] = total_users
        context['active_users'] = active_users
        context['inactive_users'] = inactive_users
        context['percentage_active'] = percentage_active
        
        # Pasar búsqueda al contexto
        context['search'] = self.request.GET.get('search', '')
        
        return context

class SimpleUserCreateView(LoginRequiredMixin, View):
    """Vista para crear usuarios - Solo para org_admin"""
    template_name = 'users/simple_create_user.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Solo org_admin pueden crear usuarios
        if not request.user.is_org_admin:
            logger.warning(f"Usuario {request.user.email} intentó crear usuario sin permisos de org_admin")
            raise PermissionDenied("No tienes permisos para crear usuarios")
        
        logger.info(f"Usuario {request.user.email} accediendo a creación de usuarios")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        logger.info(f"Mostrando formulario de creación de usuario para {request.user.email}")
        form = SimpleUserCreateForm(user=request.user)
        
        # Log de contexto del formulario
        if request.user.organization:
            limit_info = request.user.organization.can_add_user_detailed()
            logger.info(f"Límites de organización {request.user.organization.name}: {limit_info}")
        
        # Preparar contexto para JavaScript
        django_context = self._prepare_js_context(request, form)
        
        return render(request, self.template_name, {
            'form': form,
            'django_context': django_context
        })
    
    def post(self, request):
        logger.info(f"Procesando creación de usuario por {request.user.email}")
        logger.info(f"Datos POST completos: {dict(request.POST)}")
        logger.debug(f"Datos del formulario recibidos: {dict(request.POST)}")
        
        # Log específico de campos importantes
        logger.info(f"Campo 'organization_id' en POST: {request.POST.get('organization_id', 'NO_ENCONTRADO')}")
        logger.info(f"Todos los campos POST: {list(request.POST.keys())}")
        
        form = SimpleUserCreateForm(request.POST, user=request.user)
        
        # Log detallado de validación
        logger.info(f"Validando formulario de creación de usuario...")
        logger.info(f"Formulario tiene datos: {form.data}")
        
        if form.is_valid():
            logger.info("Formulario válido, procediendo a crear usuario")
            try:
                # Log antes de la creación
                cleaned_data = form.cleaned_data
                logger.info(f"Creando usuario con email: {cleaned_data.get('email')}")
                logger.info(f"Organización destino: {cleaned_data.get('organization_id')}")
                logger.info(f"Rol asignado: {cleaned_data.get('user_role')}")
                logger.info(f"Usuario activo: {cleaned_data.get('is_active')}")
                
                user, temp_password, email_sent = form.save(request)
                
                logger.info(f"Usuario creado exitosamente: ID={user.id}, Email={user.email}")
                logger.info(f"Email enviado: {email_sent}")
                
                if email_sent:
                    messages.success(
                        request,
                        f'Usuario {user.username or user.email} creado exitosamente. '
                        f'Se han enviado las credenciales por correo electrónico.'
                    )
                    logger.info(f"Mensaje de éxito mostrado al usuario")
                else:
                    messages.warning(
                        request,
                        f'Usuario {user.username or user.email} creado exitosamente, '
                        f'pero no se pudo enviar el correo electrónico. '
                        f'Credenciales: {user.email} / {temp_password}'
                    )
                    logger.warning(f"Usuario creado pero falló el envío de email")
                
                logger.info(f"Redirigiendo a lista de usuarios")
                return redirect('users:user_list')
                
            except Exception as e:
                logger.error(f"Error crítico al crear usuario: {str(e)}", exc_info=True)
                logger.error(f"Datos del formulario que causaron el error: {form.cleaned_data}")
                messages.error(request, f"Error al crear el usuario: {str(e)}")
        else:
            logger.warning(f"Formulario inválido para creación de usuario")
            logger.warning(f"Errores del formulario: {form.errors}")
            logger.warning(f"Errores no de campo: {form.non_field_errors()}")
            
            # Log detallado de cada error de campo
            for field, errors in form.errors.items():
                logger.warning(f"Error en campo '{field}': {errors}")
            
            # Log del estado de los campos del formulario
            logger.info(f"Estado de campos del formulario:")
            for field_name, field in form.fields.items():
                field_value = form.data.get(field_name, 'NO_ENVIADO')
                logger.info(f"  {field_name}: '{field_value}' (requerido: {field.required})")
        
        # Preparar contexto para JavaScript con errores
        django_context = self._prepare_js_context(request, form)
        
        logger.info("Mostrando formulario con errores al usuario")
        return render(request, self.template_name, {
            'form': form,
            'django_context': django_context
        })
    
    def _prepare_js_context(self, request, form):
        """Prepara el contexto para el JavaScript de logging"""
        context = {
            'currentUser': {
                'isOrgAdmin': request.user.is_org_admin,
                'organization': request.user.organization.name if request.user.organization else 'Sin organización',
                'email': request.user.email
            }
        }
        
        # Información de límites de organización
        if request.user.is_org_admin and request.user.organization:
            limit_info = request.user.organization.can_add_user_detailed()
            context['orgLimits'] = {
                'organization': request.user.organization.name,
                'totalUsers': limit_info['total_users'],
                'maxUsers': limit_info['max_users'],
                'activeUsers': limit_info['active_users'],
                'availableSlots': limit_info['available_slots'],
                'canAdd': limit_info['can_add']
            }
        
        # Errores del formulario
        if form.errors:
            context['formErrors'] = dict(form.errors)
        
        if form.non_field_errors():
            context['nonFieldErrors'] = list(form.non_field_errors())
        
        return context

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

class UserDeleteView(LoginRequiredMixin, View):
    """Vista para eliminar usuarios - Solo para org_admin"""
    template_name = 'users/user_delete.html'
    
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
            
            user_to_delete.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario {full_name} ({username}) eliminado exitosamente.'
            })
            
        except Exception as e:
            logger.error(f"Error al eliminar usuario: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar el usuario: {str(e)}'
            })
