# apps/users/forms_simplified.py - Formularios simplificados
from django import forms
from django.contrib.auth import get_user_model
from apps.orgs.models import Organization
from .utils import generate_random_password, send_new_user_email


User = get_user_model()


class SimpleUserCreateForm(forms.Form):
    """Formulario simplificado para crear usuarios eliminando redundancias"""
    
    # Información esencial solamente
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
    

    
    # Simplificar roles
    user_role = forms.ChoiceField(
        choices=[
            ('user', 'Usuario Normal'),
            ('admin', 'Administrador'),
        ],
        label="Rol",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.BooleanField(
        required=False, 
        initial=True,
        label="Usuario activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        self.creating_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar opciones según permisos del usuario que crea
        if self.creating_user:
            if self.creating_user.is_org_admin and self.creating_user.organization:
                # Admin de org: solo puede crear en su organización
                self.organization = self.creating_user.organization
                
                # Agregar campo oculto para la organización
                self.fields['organization_id'] = forms.CharField(
                    widget=forms.HiddenInput(),
                    initial=self.creating_user.organization.id
                )
                
                # Solo puede crear usuarios normales y admins de org
                self.fields['user_role'].choices = [
                    ('user', 'Usuario Normal'),
                    ('admin', 'Administrador de Organización'),
                ]
                self.fields['user_role'].help_text = "Como admin de organización, solo puedes crear usuarios normales y otros admins para tu organización"
            
            elif self.creating_user.is_superuser:
                # Superuser: puede crear en cualquier organización
                self.fields['organization'] = forms.ModelChoiceField(
                    queryset=Organization.objects.filter(is_active=True),
                    required=True,
                    label="Organización",
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    empty_label="Selecciona una organización"
                )
                
                # Puede crear cualquier tipo de usuario
                self.fields['user_role'].choices = [
                    ('user', 'Usuario Normal'),
                    ('admin', 'Administrador de Organización'),
                    ('superuser', 'Superusuario'),
                ]
            else:
                # Usuario sin permisos - no debería llegar aquí
                self.fields['user_role'].choices = [('user', 'Usuario Normal')]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email
    
    def clean_organization_id(self):
        """Validar organización para admins de org"""
        if hasattr(self, 'organization'):
            org_id = self.cleaned_data.get('organization_id')
            if org_id and int(org_id) != self.organization.id:
                raise forms.ValidationError("No puedes crear usuarios en otra organización.")
            return org_id
        return None
    
    def clean_organization(self):
        """Validar organización para superusers"""
        organization = self.cleaned_data.get('organization')
        
        if organization and not organization.can_add_user():
            limit_info = organization.can_add_user_detailed()
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
    
    def clean(self):
        """Validación adicional considerando el contexto"""
        cleaned_data = super().clean()
        
        # Determinar la organización según el tipo de usuario
        if self.creating_user and self.creating_user.is_org_admin:
            # Para admin de org, usar su organización
            organization = self.organization
            
            # Verificar límites para admins de org
            if organization and not organization.can_add_user():
                limit_info = organization.can_add_user_detailed()
                if limit_info['has_inactive_users']:
                    raise forms.ValidationError(
                        f"Tu organización ha alcanzado el límite de {organization.get_max_users()} usuarios. "
                        f"Actualmente tienes {limit_info['total_users']} usuarios "
                        f"({limit_info['active_users']} activos, {limit_info['inactive_users']} inactivos). "
                        f"Para crear un nuevo usuario, elimina un usuario existente o contacta con soporte."
                    )
                else:
                    raise forms.ValidationError(
                        f"Tu organización ha alcanzado el límite máximo de {organization.get_max_users()} usuarios. "
                        f"Para crear un nuevo usuario, contacta con soporte para incrementar tu límite."
                    )
        
        return cleaned_data
    
    def save(self, request=None):
        """Crear usuario simplificado"""
        password = generate_random_password()
        
        # Determinar la organización
        if self.creating_user and self.creating_user.is_org_admin:
            organization = self.organization
        else:
            organization = self.cleaned_data.get('organization')
        
        # Determinar permisos según el rol
        user_role = self.cleaned_data.get('user_role')
        is_org_admin = user_role == 'admin'
        is_superuser = user_role == 'superuser'
        is_staff = is_superuser  # Los superusers también son staff
        
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=password,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            organization=organization,
            is_active=self.cleaned_data.get('is_active', True),
            is_org_admin=is_org_admin,
            is_superuser=is_superuser,
            is_staff=is_staff
        )
        
        # Enviar credenciales
        email_sent = send_new_user_email(user, password, request)
        return user, password, email_sent


class SimpleUserEditForm(forms.ModelForm):
    """Formulario simplificado para editar usuarios"""
    
    # Campo de rol específico para edición
    user_role = forms.ChoiceField(
        label="Rol del usuario",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'is_active': 'Usuario activo',
        }
    
    def __init__(self, *args, **kwargs):
        self.editing_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar rol actual
        if self.instance:
            if self.instance.is_superuser:
                current_role = 'superuser'
            elif self.instance.is_org_admin:
                current_role = 'admin'
            else:
                current_role = 'user'
            
            # Configurar opciones según permisos del usuario que edita
            if self.editing_user and self.editing_user.is_org_admin:
                self.fields['user_role'].choices = [
                    ('user', 'Usuario Normal'),
                    ('admin', 'Administrador de Organización'),
                ]
            elif self.editing_user and self.editing_user.is_superuser:
                self.fields['user_role'].choices = [
                    ('user', 'Usuario Normal'),
                    ('admin', 'Administrador de Organización'),
                    ('superuser', 'Superusuario'),
                ]
            else:
                self.fields['user_role'].choices = [('user', 'Usuario Normal')]
            
            self.fields['user_role'].initial = current_role
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Actualizar permisos según el rol
        user_role = self.cleaned_data.get('user_role')
        user.is_org_admin = (user_role == 'admin')
        user.is_superuser = (user_role == 'superuser')
        user.is_staff = (user_role == 'superuser')
        
        if commit:
            user.save()
        
        return user 