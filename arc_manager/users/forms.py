from django import forms
from django.contrib.auth import get_user_model
from orgs.models import Organization

User = get_user_model()

class SimpleUserCreateForm(forms.Form):
    """Formulario simple para crear usuarios"""
    
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
    
    # Configuración
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
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
                self.fields['organization'].initial = user.organization
                # Deshabilitar el campo de organización para admin de org
                self.fields['organization'].widget.attrs.update({
                    'disabled': True,
                    'readonly': True
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
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data
    
    def save(self):
        """Crear el usuario con los datos del formulario"""
        cleaned_data = self.cleaned_data
        role = cleaned_data.get('user_role')
        
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
            password=cleaned_data['password'],
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            organization=cleaned_data.get('organization'),
            is_active=cleaned_data.get('is_active', True),
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_org_admin=is_org_admin
        )
        
        return user


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