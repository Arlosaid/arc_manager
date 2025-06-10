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
        """Mostrar nombre completo o email como fallback"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.email
    
    @property
    def full_name(self):
        """Nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.email
    
    @property
    def username_display(self):
        """Para compatibilidad con templates existentes"""
        return self.full_name
    
    def role_display(self):
        if self.is_org_admin:
            return "Administrador"
        else:
            return "Usuario"
    
    def can_manage_users(self):
        return self.is_org_admin
    
    def get_organization_name(self):
        return self.organization.name if self.organization else "Sin organización"
    
    def is_in_organization(self, org_id):
        return self.organization_id == org_id if self.organization else False
    
    def can_manage_organization(self):
        return self.is_org_admin and self.organization
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(is_superuser=True) | models.Q(organization__isnull=False) | models.Q(is_active=False),
                name='users_must_have_org_or_be_superuser_or_inactive'
            ),
            models.UniqueConstraint(
                fields=['email'],
                name='unique_email'
            )
        ]