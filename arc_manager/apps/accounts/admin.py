from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from .models import User


class UserCreationForm(forms.ModelForm):
    """Formulario para crear nuevos usuarios."""
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=True, label="Nombre")
    last_name = forms.CharField(required=True, label="Apellido")
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'organization')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Formulario para actualizar usuarios."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff', 
                   'is_org_admin', 'organization')

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'full_name', 'get_organization_link', 'get_role_display', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_org_admin', 'organization', 'date_joined')
    readonly_fields = ('date_joined', 'last_login', 'get_organization_link')
    
    # Acciones útiles pero simples
    actions = ['activate_users', 'deactivate_users', 'make_org_admin', 'remove_org_admin']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Organización', {'fields': ('organization', 'get_organization_link')}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_org_admin'),
            'description': 'is_org_admin: Administrador de su organización | is_staff: Acceso al admin | is_superuser: Admin total'
        }),
        ('Información del sistema', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Organización', {
            'fields': ('organization',),
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_org_admin'),
        }),
    )
    
    search_fields = ('email', 'first_name', 'last_name', 'organization__name')
    ordering = ('-date_joined',)
    
    def full_name(self, obj):
        """Muestra el nombre completo"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email
    full_name.short_description = 'Nombre completo'
    
    def get_organization_link(self, obj):
        """Link a la organización"""
        if obj.organization:
            org_url = reverse('admin:orgs_organization_change', args=[obj.organization.pk])
            return format_html('<a href="{}">{}</a>', org_url, obj.organization.name)
        return 'Sin organización'
    get_organization_link.short_description = 'Organización'
    
    def get_role_display(self, obj):
        """Muestra el rol del usuario de forma clara"""
        if obj.is_superuser:
            return format_html('<span style="color: red; font-weight: bold;">🔑 Superusuario</span>')
        elif obj.is_staff:
            return format_html('<span style="color: blue; font-weight: bold;">👔 Staff</span>')
        elif obj.is_org_admin:
            return format_html('<span style="color: green; font-weight: bold;">👨‍💼 Admin Org</span>')
        else:
            return format_html('<span style="color: gray;">👤 Usuario</span>')
    get_role_display.short_description = 'Rol'
    
    # Acciones útiles
    def activate_users(self, request, queryset):
        """Activar usuarios seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"✅ Se activaron {updated} usuarios correctamente.",
            messages.SUCCESS
        )
    activate_users.short_description = "✅ Activar usuarios"
    
    def deactivate_users(self, request, queryset):
        """Desactivar usuarios seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"❌ Se desactivaron {updated} usuarios correctamente.",
            messages.SUCCESS
        )
    deactivate_users.short_description = "❌ Desactivar usuarios"
    
    def make_org_admin(self, request, queryset):
        """Convertir en administradores de organización"""
        updated = queryset.update(is_org_admin=True)
        self.message_user(
            request,
            f"👨‍💼 Se convirtieron {updated} usuarios en administradores de organización.",
            messages.SUCCESS
        )
    make_org_admin.short_description = "👨‍💼 Hacer admin de org"
    
    def remove_org_admin(self, request, queryset):
        """Quitar permisos de administrador de organización"""
        updated = queryset.update(is_org_admin=False)
        self.message_user(
            request,
            f"👤 Se removieron permisos de admin de org a {updated} usuarios.",
            messages.SUCCESS
        )
    remove_org_admin.short_description = "👤 Quitar admin de org"

# Registrar el modelo User
admin.site.register(User, UserAdmin)