# App de Organizaciones

Esta app maneja toda la funcionalidad relacionada con organizaciones en el sistema multitenant.

## Características

### Modelo Organization
- **name**: Nombre de la organización
- **slug**: Identificador único para URLs
- **description**: Descripción opcional
- **is_active**: Estado activo/inactivo
- **max_users**: Límite máximo de usuarios
- **created_at/updated_at**: Timestamps automáticos

### Funcionalidades

#### Para Superusuarios
- Crear, editar y ver todas las organizaciones
- Gestionar usuarios de cualquier organización
- Acceso completo al admin de Django

#### Para Administradores de Organización
- Ver y editar su propia organización
- Gestionar usuarios de su organización
- Ver estadísticas de su organización

#### Para Usuarios Normales
- Ver información de su organización
- Ver otros usuarios de su organización

## Uso

### Crear una organización desde línea de comandos
```bash
python manage.py create_organization "Mi Empresa" --description "Descripción de mi empresa" --max-users 50
```

### URLs disponibles
- `/organizaciones/` - Lista de organizaciones (solo superusuarios)
- `/organizaciones/crear/` - Crear organización (solo superusuarios)
- `/organizaciones/<id>/` - Ver detalles de organización
- `/organizaciones/<id>/editar/` - Editar organización
- `/organizaciones/mi-organizacion/` - Ver mi organización

### Mixins disponibles

#### OrganizationMixin
Filtra automáticamente los querysets por la organización del usuario.

```python
from orgs.mixins import OrganizationMixin

class MiVistaListView(OrganizationMixin, ListView):
    model = MiModelo
```

#### OrganizationRequiredMixin
Requiere que el usuario tenga una organización asignada.

```python
from orgs.mixins import OrganizationRequiredMixin

class MiVista(OrganizationRequiredMixin, TemplateView):
    template_name = 'mi_template.html'
```

#### OrganizationAdminMixin
Requiere permisos de administrador de organización.

```python
from orgs.mixins import OrganizationAdminMixin

class MiVistaAdmin(OrganizationAdminMixin, UpdateView):
    model = MiModelo
```

## Middleware

El `OrganizationMiddleware` agrega automáticamente `request.user_organization` a todas las requests.

## Integración con otros modelos

Para hacer que un modelo sea específico de organización, agrega:

```python
class MiModelo(models.Model):
    organization = models.ForeignKey(
        'orgs.Organization',
        on_delete=models.CASCADE,
        related_name='mi_modelos'
    )
    # ... otros campos
```

Luego usa `OrganizationMixin` en tus vistas para filtrar automáticamente.