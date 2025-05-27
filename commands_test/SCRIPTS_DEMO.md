# 🚀 Scripts de Gestión de Datos de Demo

Este conjunto de scripts te permite gestionar fácilmente organizaciones y usuarios de ejemplo para desarrollo y testing.

## 📁 Archivos Incluidos

### 1. Comandos de Django (`orgs/management/commands/`)

- **`setup_demo_data.py`** - Crear datos completos de ejemplo
- **`create_user.py`** - Crear usuarios individuales
- **`create_organization.py`** - Crear organizaciones (ya existía)
- **`list_orgs.py`** - Listar organizaciones y usuarios

### 2. Script Interactivo

- **`scripts_demo.py`** - Menú interactivo para todas las operaciones

## 🎯 Uso Rápido

### Opción 1: Script Interactivo (Recomendado)

```bash
python scripts_demo.py
```

Este script te mostrará un menú interactivo con todas las opciones disponibles.

### Opción 2: Comandos Individuales

#### Crear datos de ejemplo completos
```bash
# Crear 3 organizaciones con 5 usuarios cada una
python manage.py setup_demo_data

# Personalizar cantidad
python manage.py setup_demo_data --orgs=5 --users-per-org=8

# Limpiar datos existentes primero
python manage.py setup_demo_data --reset --orgs=3 --users-per-org=5
```

#### Crear una organización
```bash
# Básico
python manage.py create_organization "Mi Empresa"

# Con opciones
python manage.py create_organization "TechCorp" --description="Empresa de tecnología" --max-users=20
```

#### Crear un usuario
```bash
# Usuario básico
python manage.py create_user usuario@ejemplo.com

# Usuario con organización
python manage.py create_user admin@techcorp.com --name="Juan Pérez" --org-slug=techcorp --admin

# Superusuario
python manage.py create_user super@admin.com --superuser
```

#### Listar datos
```bash
# Resumen general
python manage.py list_orgs

# Información detallada
python manage.py list_orgs --detailed

# Solo una organización
python manage.py list_orgs --org-slug=techcorp --detailed

# Usuarios sin organización
python manage.py list_orgs --users-only
```

## 📊 Datos de Ejemplo Generados

### Organizaciones Predefinidas
1. **TechCorp Solutions** - Empresa de desarrollo de software
2. **Marketing Digital Pro** - Agencia de marketing digital  
3. **Consultores Financieros** - Servicios financieros
4. **Diseño Creativo Studio** - Estudio de diseño
5. **Educación Online** - Plataforma educativa

### Usuarios Generados
- **Nombres realistas** en español
- **Emails únicos** basados en nombre + organización
- **Contraseña por defecto**: `demo123`
- **Primer usuario** de cada organización es **administrador**
- **Resto** son usuarios regulares

## 🔧 Opciones Avanzadas

### Comando `setup_demo_data`
```bash
python manage.py setup_demo_data [opciones]

Opciones:
  --reset              Eliminar datos existentes primero
  --orgs=N            Número de organizaciones (default: 3)
  --users-per-org=N   Usuarios por organización (default: 5)
```

### Comando `create_user`
```bash
python manage.py create_user EMAIL [opciones]

Opciones:
  --name=NOMBRE       Nombre completo del usuario
  --password=PASS     Contraseña (default: demo123)
  --org-slug=SLUG     Slug de la organización
  --org-id=ID         ID de la organización
  --admin             Hacer administrador de organización
  --superuser         Crear como superusuario
  --inactive          Crear como inactivo
```

### Comando `list_orgs`
```bash
python manage.py list_orgs [opciones]

Opciones:
  --detailed          Mostrar información detallada
  --org-slug=SLUG     Mostrar solo una organización
  --users-only        Mostrar solo usuarios sin organización
```

## 💡 Casos de Uso Comunes

### 1. Configuración inicial para desarrollo
```bash
# Limpiar y crear datos frescos
python manage.py setup_demo_data --reset --orgs=3 --users-per-org=5
```

### 2. Agregar una nueva organización con admin
```bash
# Crear organización
python manage.py create_organization "Nueva Empresa" --max-users=15

# Crear admin para esa organización
python manage.py create_user admin@nuevaempresa.com --name="Admin Principal" --org-slug=nueva-empresa --admin
```

### 3. Testing con usuarios específicos
```bash
# Usuario normal
python manage.py create_user test@usuario.com --org-slug=techcorp

# Usuario inactivo
python manage.py create_user inactivo@test.com --org-slug=techcorp --inactive

# Superusuario para testing
python manage.py create_user super@test.com --superuser
```

### 4. Verificar estado del sistema
```bash
# Ver resumen
python manage.py list_orgs

# Ver detalles de una organización específica
python manage.py list_orgs --org-slug=techcorp --detailed

# Encontrar usuarios sin asignar
python manage.py list_orgs --users-only
```

## 🎨 Características del Script Interactivo

El script `scripts_demo.py` incluye:

- **Menú visual** con emojis y colores
- **Validación de entrada** para evitar errores
- **Confirmaciones** para operaciones destructivas
- **Resúmenes informativos** después de cada operación
- **Manejo de errores** con mensajes claros

## 🔒 Seguridad

- Los **superusuarios nunca se eliminan** en operaciones de limpieza
- Las **contraseñas por defecto** son solo para desarrollo
- Se **validan límites** de usuarios por organización
- Se **previenen duplicados** de emails y slugs

## 🚨 Notas Importantes

1. **Solo para desarrollo**: Estos scripts están diseñados para entornos de desarrollo
2. **Contraseñas simples**: La contraseña por defecto `demo123` es insegura
3. **Datos de prueba**: Los nombres y emails son ficticios
4. **Limpieza cuidadosa**: Los superusuarios se preservan en operaciones de reset

## 📝 Ejemplos de Salida

### Creación de datos de ejemplo:
```
🎉 Datos de ejemplo creados exitosamente!
📊 Resumen:
   • Organizaciones: 3
   • Usuarios totales: 15

📝 Credenciales de acceso:
   • Contraseña para todos los usuarios: demo123
   • Los primeros usuarios de cada organización son administradores

👥 Algunos usuarios de ejemplo:
   • ana.garcia@techcorp-solutions.com (Admin de TechCorp Solutions)
   • carlos.lopez@techcorp-solutions.com (Usuario de TechCorp Solutions)
```

### Listado de organizaciones:
```
📊 RESUMEN DEL SISTEMA
==================================================
🏢 Organizaciones totales: 3
👥 Usuarios totales: 15
✅ Usuarios asignados: 15
❌ Usuarios sin organización: 0

✅ TechCorp Solutions (slug: techcorp-solutions)
   📝 Empresa de desarrollo de software y consultoría tecnológica
   👥 Usuarios: 5/20
   👑 Administradores: 1
```

¡Estos scripts te harán la vida mucho más fácil para gestionar datos de prueba! 🎉 