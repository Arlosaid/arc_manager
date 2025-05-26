from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField("Correo electrónico", unique=True)
    username = models.CharField("Nombre de usuario", max_length=150, unique=False, blank=True, null=True)
    is_org_admin = models.BooleanField("Administrador de organización", default=False)
    organization = models.ForeignKey(
        'orgs.Organization', 
        on_delete=models.CASCADE, 
        related_name='users',
        verbose_name="Organización",
        null=True, 
        blank=True
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username or self.email
    
    def is_superadmin(self):
        return self.is_superuser
    
    def role_display(self):
        if self.is_superuser:
            return "Superadministrador"
        elif self.is_org_admin:
            return "Administrador"
        else:
            return "Usuario"
    
    def can_manage_users(self):
        return self.is_superuser or self.is_org_admin
    
    def get_organization_name(self):
        return self.organization.name if self.organization else "Sin organización"
    
    def is_in_organization(self, org_id):
        return self.organization_id == org_id if self.organization else False
    
    def can_manage_organization(self):
        return self.is_superuser or (self.is_org_admin and self.organization)