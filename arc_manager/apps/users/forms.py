from django import forms
from django.contrib.auth import get_user_model
from apps.orgs.models import Organization
from .utils import generate_random_password, send_new_user_email


User = get_user_model()

class SimpleUserCreateForm(forms.Form):
    """Formulario simple para crear usuarios con contraseña generada automáticamente"""
    
    # Información básica
    first_name = forms.CharField(
        max_length=50,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'})
    )
    last_name = forms.CharField(
        max_length=50,
        label="Apellido", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'})
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'juan.perez@empresa.com'})
    )
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'juan.perez'})
    )
    
    # Organización
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        label="Organización",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Selecciona una organización (opcional)"
    )
    
    # Permisos - Ahora con opciones más específicas
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Usuario activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Campo de rol específico
    user_role = forms.ChoiceField(
        label="Rol del usuario",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Selecciona el rol que tendrá el usuario en el sistema"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Guardar referencia al usuario que está creando para usar en validaciones
        self._creating_user = user
        
        # Configurar opciones según permisos del usuario que crea
        if user:
            if user.is_superuser:
                # Superuser puede elegir cualquier organización y crear cualquier rol
                self.fields['organization'].queryset = Organization.objects.all()
                self.fields['user_role'].choices = [
                    ('normal', 'Usuario Normal'),
                    ('org_admin', 'Administrador de Organización'),
                    ('superuser', 'Superusuario'),
                ]
            elif user.is_org_admin and user.organization:
                # Admin de org solo puede crear en su organización y roles limitados
                self.fields['organization'].queryset = Organization.objects.filter(
                    id=user.organization.id
                )
                
                # IMPORTANTE: Para admins de org, siempre establecer su organización
                self.fields['organization'].initial = user.organization
                
                # En lugar de disabled, usar readonly para que el valor se envíe en POST
                self.fields['organization'].widget.attrs.update({
                    'readonly': True
                })
                
                # Agregar JavaScript para evitar que el usuario cambie la selección
                self.fields['organization'].widget.attrs.update({
                    'onchange': 'this.selectedIndex = 0;',  # Resetea a la primera opción si intenta cambiar
                    'style': 'pointer-events: none; background-color: #e9ecef;'  # Apariencia de deshabilitado
                })
                
                # Solo puede crear admin de org y usuarios normales
                self.fields['user_role'].choices = [
                    ('normal', 'Usuario Normal'),
                    ('org_admin', 'Administrador de Organización'),
                ]
                # Agregar ayuda contextual
                self.fields['user_role'].help_text = "Como admin de organización, solo puedes crear usuarios normales y otros admins para tu organización"
            else:
                # Usuario sin permisos
                self.fields['organization'].queryset = Organization.objects.none()
                self.fields['user_role'].choices = []

        # NUEVO: Preservar valores en caso de errores de validación
        self._preserve_form_values()
    
    def _preserve_form_values(self):
        """Preserva los valores del formulario cuando hay errores de validación"""
        if self.data:
            # Preservar el estado del checkbox is_active
            # En Django, los checkboxes no marcados no se envían en POST
            if 'is_active' not in self.data:
                # Si no está en POST data, significa que está desmarcado
                self.fields['is_active'].initial = False
            else:
                # Si está en POST data, está marcado
                self.fields['is_active'].initial = True
            
            # Preservar la organización seleccionada
            if 'organization' in self.data and self.data['organization']:
                try:
                    org_id = int(self.data['organization'])
                    if self.fields['organization'].queryset.filter(id=org_id).exists():
                        self.fields['organization'].initial = org_id
                except (ValueError, TypeError):
                    pass
            
            # Preservar el rol seleccionado
            if 'user_role' in self.data:
                user_role = self.data['user_role']
                # Verificar que el rol está en las opciones disponibles
                available_roles = [choice[0] for choice in self.fields['user_role'].choices]
                if user_role in available_roles:
                    self.fields['user_role'].initial = user_role
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con este nombre de usuario.")
        return username
    
    def clean_organization(self):
        """Validar que la organización puede aceptar un nuevo usuario"""
        organization = self.cleaned_data.get('organization')
        
        # IMPORTANTE: Para admins de org, si no hay organización en cleaned_data,
        # usar la organización del usuario que está creando
        if not organization and hasattr(self, '_creating_user') and self._creating_user and self._creating_user.is_org_admin:
            organization = self._creating_user.organization
            # Actualizar cleaned_data para que el resto de validaciones funcionen
            self.cleaned_data['organization'] = organization
        
        # Validar límite de usuarios (activos e inactivos) si hay organización
        if organization:
            limit_info = organization.can_add_user_detailed()
            
            if not limit_info['can_add']:
                # Para admins de org, marcar que hay error de límite para manejarlo en clean()
                if hasattr(self, '_creating_user') and self._creating_user and self._creating_user.is_org_admin:
                    # Marcar que hay error de límite para manejarlo en clean()
                    self._org_limit_error = {
                        'organization': organization,
                        'limit_info': limit_info
                    }
                    # NO lanzar excepción aquí para admins de org
                else:
                    # Para superusuarios, mostrar error normal en el campo
                    if limit_info['has_inactive_users']:
                        raise forms.ValidationError(
                            f"La organización '{organization.name}' ha alcanzado su límite de "
                            f"{organization.get_max_users()} usuarios. "
                            f"Actualmente tiene {limit_info['total_users']} usuarios "
                            f"({limit_info['active_users']} activos, {limit_info['inactive_users']} inactivos). "
                            f"Para crear un nuevo usuario, elimina un usuario existente "
                            f"o incrementa el límite de la organización."
                        )
                    else:
                        raise forms.ValidationError(
                            f"La organización '{organization.name}' ha alcanzado su límite máximo de "
                            f"{organization.get_max_users()} usuarios. "
                            f"Para crear un nuevo usuario, incrementa el límite de la organización."
                        )
        
        return organization
    
    def clean_is_active(self):
        """Validación específica para el campo is_active"""
        # Django no envía checkboxes desmarcados en POST data
        # Si el campo no está en self.data, significa que está desmarcado
        is_active = self.cleaned_data.get('is_active', False)
        return is_active
    
    def clean(self):
        """Validación adicional que considera todos los campos juntos"""
        cleaned_data = super().clean()
        organization = cleaned_data.get('organization')
        
        # Obtener is_active de manera más robusta
        # Si 'is_active' no está en self.data (POST data), significa que el checkbox está desmarcado
        if 'is_active' in self.data:
            is_active = cleaned_data.get('is_active', False)
        else:
            is_active = False  # Checkbox desmarcado
            
        user_role = cleaned_data.get('user_role')
        
        # Los superusuarios pueden existir sin organización (activos o inactivos)
        if user_role == 'superuser':
            return cleaned_data
        
        # IMPORTANTE: Manejar error de límite de organización para admins de org
        if hasattr(self, '_org_limit_error') and hasattr(self, '_creating_user') and self._creating_user and self._creating_user.is_org_admin:
            # Hay un error de límite marcado en clean_organization
            error_org = self._org_limit_error['organization']
            limit_info = self._org_limit_error['limit_info']
            
            self.add_error(None, 
                f"❌ No se puede crear el usuario. "
                f"Tu organización '{error_org.name}' ha alcanzado su límite de "
                f"{error_org.get_max_users()} usuarios. "
                f"Actualmente tienes {limit_info['total_users']} usuarios "
                f"({limit_info['active_users']} activos, {limit_info['inactive_users']} inactivos). "
                f"💡 Sugerencia: Elimina un usuario existente o contacta al administrador para incrementar el límite."
            )
            # El formulario será inválido por este error
            return cleaned_data
        
        # IMPORTANTE: Solo validar organización obligatoria si NO hay errores en el campo organization
        # Esto evita el doble error cuando la organización está en límite
        if 'organization' not in self.errors:
            # Para usuarios activos que no son superusuarios, la organización es obligatoria
            if is_active and not organization:
                # EXCEPCIÓN: Para admins de org, usar su organización automáticamente
                if hasattr(self, '_creating_user') and self._creating_user and self._creating_user.is_org_admin:
                    organization = self._creating_user.organization
                    cleaned_data['organization'] = organization
                else:
                    self.add_error('organization', 
                        "Los usuarios activos deben pertenecer a una organización. "
                        "Selecciona una organización o marca el usuario como inactivo."
                    )
                    return cleaned_data
        
        # Información adicional para usuarios con organización
        if organization:
            limit_info = organization.can_add_user_detailed()
            
            if not limit_info['can_add']:
                # Agregar información útil para el usuario (solo para superusuarios, ya que para admins se maneja arriba)
                if not (hasattr(self, '_creating_user') and self._creating_user and self._creating_user.is_org_admin):
                    if limit_info['has_inactive_users']:
                        self.add_error(None, 
                            f"💡 Sugerencia: La organización '{organization.name}' tiene "
                            f"{limit_info['inactive_users']} usuario(s) inactivo(s). "
                            f"Puedes eliminar uno de ellos para hacer espacio."
                        )
        
        return cleaned_data
    
    def save(self, request=None):
        """Crear el usuario con los datos del formulario y contraseña generada automáticamente"""
        cleaned_data = self.cleaned_data
        role = cleaned_data.get('user_role')
        
        # Generar contraseña aleatoria
        temp_password = generate_random_password()
        
        # Configurar permisos según el rol seleccionado
        is_superuser = False
        is_staff = False
        is_org_admin = False
        
        if role == 'superuser':
            is_superuser = True
            is_staff = True
            is_org_admin = False
        elif role == 'org_admin':
            is_superuser = False
            is_staff = False
            is_org_admin = True
        else:  # normal
            is_superuser = False
            is_staff = False
            is_org_admin = False
        
        user = User.objects.create_user(
            email=cleaned_data['email'],
            username=cleaned_data['username'],
            password=temp_password,
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            organization=cleaned_data.get('organization'),
            is_active=cleaned_data.get('is_active', True),
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_org_admin=is_org_admin
        )
        
        # SIEMPRE enviar email con las credenciales (ya que el email es necesario para login)
        email_sent = send_new_user_email(user, temp_password, request)
        user.email_sent = email_sent
        
        return user, temp_password, email_sent  # Retornamos también si se envió el email


# El resto de la clase UserEditForm permanece igual...
class UserEditForm(forms.ModelForm):
    """Formulario para editar usuarios existentes"""
    
    # Campo de rol específico para edición
    user_role = forms.ChoiceField(
        label="Rol del usuario",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Cambia el rol del usuario en el sistema"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'organization', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'username': 'Nombre de usuario',
            'organization': 'Organización',
            'is_active': 'Usuario activo',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Usuario que está editando
        super().__init__(*args, **kwargs)
        
        # Configurar rol actual
        if self.instance.is_superuser:
            current_role = 'superuser'
        elif self.instance.is_org_admin:
            current_role = 'org_admin'
        else:
            current_role = 'normal'
        
        # Filtrar organizaciones y roles según permisos
        if user:
            if user.is_superuser:
                # Superuser puede cambiar a cualquier organización y rol
                self.fields['organization'].queryset = Organization.objects.all()
                self.fields['user_role'].choices = [
                    ('normal', 'Usuario Normal'),
                    ('org_admin', 'Administrador de Organización'),
                    ('superuser', 'Superusuario'),
                ]
            elif user.is_org_admin and user.organization:
                # Admin de org solo puede asignar a su organización y roles limitados
                self.fields['organization'].queryset = Organization.objects.filter(
                    id=user.organization.id
                )
                # Solo puede cambiar entre admin de org y usuario normal
                self.fields['user_role'].choices = [
                    ('normal', 'Usuario Normal'),
                    ('org_admin', 'Administrador de Organización'),
                ]
                self.fields['user_role'].help_text = "Como admin de organización, solo puedes asignar roles de usuario normal o admin de organización"
            else:
                # Usuario normal no puede cambiar organización ni roles
                self.fields['organization'].widget.attrs['readonly'] = True
                self.fields['user_role'].widget.attrs['disabled'] = True
                self.fields['user_role'].choices = [(current_role, 'Sin permisos para cambiar')]
        
        # Establecer el rol actual
        self.fields['user_role'].initial = current_role
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro usuario con este email.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro usuario con este nombre de usuario.")
        return username
    
    def clean_organization(self):
        """Validar cambios de organización considerando límites de usuarios"""
        new_organization = self.cleaned_data.get('organization')
        current_organization = self.instance.organization
        is_active = self.cleaned_data.get('is_active', self.instance.is_active)
        
        # Si no hay cambio de organización, no validar
        if new_organization == current_organization:
            return new_organization
        
        # Si el usuario va a estar en la nueva organización, validar límites
        if new_organization and is_active:
            limit_info = new_organization.can_add_user_detailed()
            
            if not limit_info['can_add']:
                if limit_info['has_inactive_users']:
                    raise forms.ValidationError(
                        f"No se puede asignar el usuario a la organización '{new_organization.name}' "
                        f"porque ha alcanzado su límite de {new_organization.get_max_users()} usuarios. "
                        f"Actualmente tiene {limit_info['total_users']} usuarios "
                        f"({limit_info['active_users']} activos, {limit_info['inactive_users']} inactivos). "
                        f"Para asignar este usuario, elimina un usuario de esa organización "
                        f"o incrementa el límite de la organización."
                    )
                else:
                    raise forms.ValidationError(
                        f"No se puede asignar el usuario a la organización '{new_organization.name}' "
                        f"porque ha alcanzado su límite máximo de {new_organization.get_max_users()} usuarios. "
                        f"Para asignar este usuario, incrementa el límite de la organización."
                    )
        
        return new_organization
    
    def clean(self):
        """Validación adicional que considera todos los campos juntos"""
        cleaned_data = super().clean()
        new_organization = cleaned_data.get('organization')
        current_organization = self.instance.organization
        new_is_active = cleaned_data.get('is_active', self.instance.is_active)
        current_is_active = self.instance.is_active
        user_role = cleaned_data.get('user_role')
        
        # Caso: Usuario inactivo que se va a activar en la misma organización
        if (new_organization == current_organization and 
            current_organization and 
            not current_is_active and 
            new_is_active):
            
            limit_info = current_organization.can_add_user_detailed()
            
            if not limit_info['can_add']:
                self.add_error('is_active',
                    f"No se puede activar el usuario porque la organización '{current_organization.name}' "
                    f"ha alcanzado su límite de {current_organization.get_max_users()} usuarios. "
                    f"Actualmente tiene {limit_info['total_users']} usuarios "
                    f"({limit_info['active_users']} activos, {limit_info['inactive_users']} inactivos)."
                )
        
        # Caso: Usuario que se mueve a nueva organización
        if (new_organization != current_organization and 
            new_organization and 
            new_is_active):
            
            limit_info = new_organization.can_add_user_detailed()
            
            if not limit_info['can_add']:
                # Agregar información útil para el usuario
                if limit_info['has_inactive_users']:
                    self.add_error(None, 
                        f"💡 Sugerencia: La organización '{new_organization.name}' tiene "
                        f"{limit_info['inactive_users']} usuario(s) inactivo(s). "
                        f"Puedes eliminar uno de ellos para hacer espacio."
                    )
        
        # Los superusuarios pueden existir sin organización
        if user_role == 'superuser':
            return cleaned_data
        
        # Para usuarios activos que no son superusuarios, la organización es obligatoria
        if new_is_active and not new_organization:
            self.add_error('organization', 
                "Los usuarios activos deben pertenecer a una organización. "
                "Selecciona una organización o marca el usuario como inactivo."
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Aplicar el rol seleccionado
        role = self.cleaned_data.get('user_role')
        
        if role == 'superuser':
            user.is_superuser = True
            user.is_staff = True
            user.is_org_admin = False
        elif role == 'org_admin':
            user.is_superuser = False
            user.is_staff = False
            user.is_org_admin = True
        else:  # normal
            user.is_superuser = False
            user.is_staff = False
            user.is_org_admin = False
        
        if commit:
            user.save()
        return user