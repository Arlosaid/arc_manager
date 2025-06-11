from django import forms
from django.contrib.auth import get_user_model
from apps.orgs.models import Organization
from .utils import generate_random_password, send_new_user_email
import logging


User = get_user_model()
logger = logging.getLogger(__name__)

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
    
    # Organización como campo oculto (ID)
    organization_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    # Permisos - Solo usuarios normales y org_admin
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Usuario activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Campo de rol específico (sin superuser)
    user_role = forms.ChoiceField(
        label="Rol del usuario",
        choices=[
            ('normal', 'Usuario Normal'),
            ('org_admin', 'Administrador de Organización'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Selecciona el rol que tendrá el usuario en el sistema"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        logger.info(f"Inicializando formulario con usuario: {user}")
        logger.info(f"¿Es org_admin?: {user.is_org_admin if user else 'Usuario None'}")
        logger.info(f"Organización del usuario: {user.organization if user else 'Usuario None'}")
        
        # Guardar referencia al usuario que está creando
        self._creating_user = user
        
        # Configurar organization_id según permisos del usuario que crea
        if user and user.is_org_admin and user.organization:
            logger.info(f"Configurando formulario para org_admin de {user.organization.name}")
            # Admin de org solo puede crear en su organización
            self.fields['organization_id'].initial = user.organization.id
            logger.info(f"organization_id inicial establecido: {user.organization.id}")
        elif user and user.is_superuser:
            logger.info("Usuario es superuser - organization_id se debe establecer en la vista")
            # Para superusers, la vista debe proporcionar el organization_id
            pass
        else:
            logger.warning("Usuario sin permisos para crear usuarios")
        
        # Preservar valores en caso de errores
        self._preserve_form_values()
        
        logger.info("Formulario inicializado correctamente")
    
    def _preserve_form_values(self):
        """Preserva los valores del formulario cuando hay errores de validación"""
        if self.data:
            if 'is_active' not in self.data:
                self.fields['is_active'].initial = False
            else:
                self.fields['is_active'].initial = True
            
            if 'organization_id' in self.data and self.data['organization_id']:
                try:
                    org_id = int(self.data['organization_id'])
                    self.fields['organization_id'].initial = org_id
                except (ValueError, TypeError):
                    pass
            
            if 'user_role' in self.data:
                user_role = self.data['user_role']
                if user_role in ['normal', 'org_admin']:
                    self.fields['user_role'].initial = user_role
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        logger.debug(f"Validando email: {email}")
        
        if email and User.objects.filter(email=email).exists():
            logger.warning(f"Email duplicado detectado: {email}")
            raise forms.ValidationError("Ya existe un usuario con este email.")
        
        logger.debug(f"Email válido: {email}")
        return email
    
    def clean_organization_id(self):
        """Validar organization_id y convertir a objeto Organization"""
        organization_id = self.cleaned_data.get('organization_id')
        logger.debug(f"Validando organization_id: {organization_id}")
        
        if not organization_id:
            logger.error("organization_id no especificado")
            raise forms.ValidationError("La organización es obligatoria.")
        
        # Verificar que la organización existe
        try:
            organization = Organization.objects.get(id=organization_id)
            logger.debug(f"Organización encontrada: {organization}")
        except Organization.DoesNotExist:
            logger.error(f"Organización con ID {organization_id} no existe")
            raise forms.ValidationError("La organización especificada no existe.")
        
        # Verificar permisos del usuario que está creando
        if hasattr(self, '_creating_user') and self._creating_user:
            if self._creating_user.is_org_admin:
                # Admin de org solo puede crear en su organización
                if organization != self._creating_user.organization:
                    logger.error(f"Org admin intentando crear en organización diferente: {organization} vs {self._creating_user.organization}")
                    raise forms.ValidationError("No tienes permisos para crear usuarios en esta organización.")
        
        # Validar límite de usuarios
        logger.info(f"Verificando límites de usuarios para organización: {organization}")
        limit_info = organization.can_add_user_detailed()
        logger.info(f"Información de límites: {limit_info}")
        
        if not limit_info['can_add']:
            logger.warning(f"Límite de usuarios alcanzado para organización {organization}: {limit_info}")
            if hasattr(self, '_creating_user') and self._creating_user and self._creating_user.is_org_admin:
                self._org_limit_error = {
                    'organization': organization,
                    'limit_info': limit_info
                }
                logger.info("Guardando error de límite para mostrar mensaje detallado")
            else:
                error_msg = f"La organización '{organization.name}' ha alcanzado su límite de {organization.get_max_users()} usuarios."
                logger.error(error_msg)
                raise forms.ValidationError(error_msg)
        
        logger.debug(f"organization_id válido: {organization_id}")
        # Guardar el objeto organización para usar en save()
        self._organization = organization
        return organization_id
    
    def clean_is_active(self):
        """Validación del campo is_active"""
        is_active = self.cleaned_data.get('is_active', False)
        logger.debug(f"Campo is_active: {is_active}")
        return is_active
    
    def clean(self):
        """Validación adicional"""
        logger.info("Ejecutando validación general del formulario")
        cleaned_data = super().clean()
        
        # Manejar error de límite para admins de org
        if hasattr(self, '_org_limit_error'):
            error_org = self._org_limit_error['organization']
            limit_info = self._org_limit_error['limit_info']
            
            error_message = (
                f"❌ No se puede crear el usuario. "
                f"Tu organización '{error_org.name}' ha alcanzado su límite de "
                f"{error_org.get_max_users()} usuarios. "
                f"Actualmente tienes {limit_info['total_users']} usuarios "
                f"({limit_info['active_users']} activos, {limit_info['inactive_users']} inactivos)."
            )
            
            logger.error(f"Error de límite de organización: {error_message}")
            self.add_error(None, error_message)
        
        logger.info(f"Validación general completada. Datos limpios: {len(cleaned_data)} campos")
        return cleaned_data
    
    def save(self, request=None):
        """Crear el usuario con los datos del formulario"""
        logger.info("Iniciando proceso de guardado de usuario")
        cleaned_data = self.cleaned_data
        role = cleaned_data.get('user_role')
        
        logger.info(f"Datos para crear usuario: email={cleaned_data['email']}, role={role}")
        
        # Generar contraseña aleatoria
        temp_password = generate_random_password()
        logger.info("Contraseña temporal generada")
        
        # Configurar permisos según el rol (SOLO normal y org_admin)
        is_org_admin = (role == 'org_admin')
        logger.info(f"Configurando permisos: is_org_admin={is_org_admin}")
        
        try:
            user = User.objects.create_user(
                email=cleaned_data['email'],
                password=temp_password,
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                organization=self._organization,  # Usar el objeto organización validado
                is_active=cleaned_data.get('is_active', True),
                is_superuser=False,  # NUNCA crear superusers desde la app
                is_staff=False,      # NUNCA crear staff desde la app
                is_org_admin=is_org_admin
            )
            logger.info(f"Usuario creado en la base de datos: ID={user.id}")
            
            # Enviar email con credenciales
            logger.info("Intentando enviar email con credenciales")
            email_sent = send_new_user_email(user, temp_password, request)
            user.email_sent = email_sent
            logger.info(f"Resultado del envío de email: {email_sent}")
            
            return user, temp_password, email_sent
            
        except Exception as e:
            logger.error(f"Error en el proceso de guardado: {str(e)}", exc_info=True)
            raise


class UserEditForm(forms.ModelForm):
    """Formulario para editar usuarios existentes"""
    
    # Campo de rol específico para edición (sin superuser)
    user_role = forms.ChoiceField(
        label="Rol del usuario",
        choices=[
            ('normal', 'Usuario Normal'),
            ('org_admin', 'Administrador de Organización'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Cambia el rol del usuario en el sistema"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'organization', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'organization': 'Organización',
            'is_active': 'Usuario activo',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar rol actual (excluyendo superuser)
        if self.instance.is_org_admin:
            current_role = 'org_admin'
        else:
            current_role = 'normal'
        
        # Filtrar organizaciones según permisos
        if user and user.is_org_admin and user.organization:
            # Admin de org solo puede asignar a su organización
            self.fields['organization'].queryset = Organization.objects.filter(
                id=user.organization.id
            )
        
        # Establecer el rol actual
        self.fields['user_role'].initial = current_role
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe otro usuario con este email.")
        return email
    
    def clean_organization(self):
        """Validar cambios de organización considerando límites"""
        new_organization = self.cleaned_data.get('organization')
        current_organization = self.instance.organization
        is_active = self.cleaned_data.get('is_active', self.instance.is_active)
        
        # La organización siempre es obligatoria para usuarios de la app
        if not new_organization:
            raise forms.ValidationError("La organización es obligatoria para todos los usuarios.")
        
        # Si no hay cambio de organización, no validar límites
        if new_organization == current_organization:
            return new_organization
        
        # Si el usuario va a estar activo en la nueva organización, validar límites
        if new_organization and is_active:
            limit_info = new_organization.can_add_user_detailed()
            
            if not limit_info['can_add']:
                raise forms.ValidationError(
                    f"No se puede asignar el usuario a la organización '{new_organization.name}' "
                    f"porque ha alcanzado su límite de {new_organization.get_max_users()} usuarios."
                )
        
        return new_organization
    
    def clean(self):
        """Validación adicional"""
        cleaned_data = super().clean()
        new_organization = cleaned_data.get('organization')
        current_organization = self.instance.organization
        new_is_active = cleaned_data.get('is_active', self.instance.is_active)
        current_is_active = self.instance.is_active
        
        # Usuario inactivo que se va a activar en la misma organización
        if (new_organization == current_organization and 
            current_organization and 
            not current_is_active and 
            new_is_active):
            
            limit_info = current_organization.can_add_user_detailed()
            
            if not limit_info['can_add']:
                self.add_error('is_active',
                    f"No se puede activar el usuario porque la organización '{current_organization.name}' "
                    f"ha alcanzado su límite de {current_organization.get_max_users()} usuarios."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar los cambios del usuario"""
        user = super().save(commit=False)
        
        # Aplicar el rol seleccionado (SOLO normal y org_admin)
        role = self.cleaned_data.get('user_role')
        
        if role == 'org_admin':
            user.is_org_admin = True
        else:  # normal
            user.is_org_admin = False
        
        # NUNCA crear superusers o staff desde la app
        user.is_superuser = False
        user.is_staff = False
        
        if commit:
            user.save()
        
        return user