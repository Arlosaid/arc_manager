# 🧪 Cómo Probar el Sistema de Upgrades Corregido

## 🚀 Resumen de los Cambios Aplicados

### ✅ Problemas Solucionados:
1. **Cambio automático de planes** - Ya no es posible desde el admin de organizaciones
2. **Flujo de aprobación** - Ahora funciona correctamente al cambiar estados
3. **Emails automáticos** - Se envían cuando cambias estados en el admin
4. **Guías visuales** - El admin tiene ayuda contextual para cada estado

## 🔄 Proceso Actualizado

### 1. Usuario Solicita Upgrade ✨
```
Usuario Dashboard → "Solicitar Upgrade" → Llenar formulario → Enviar
```
- El usuario ve planes disponibles
- Llena sus datos de contacto
- Solicitud queda en estado **"Pendiente"** 🟠

### 2. Admin Aprueba ✅
```
Admin → Plans → Solicitudes de Upgrade → Cambiar estado a "Aprobada"
```
- Se envía automáticamente email con datos bancarios
- Usuario recibe instrucciones de pago

### 3. Usuario Paga 💳
```
Usuario → Hace transferencia → Envía comprobante por email/WhatsApp
```

### 4. Admin Verifica y Completa 🎯
```
Admin → Anotar referencia de pago → Cambiar estado a "Completada"
```
- Se actualiza automáticamente el plan
- Se envía email de confirmación
- Se registra en historial de pagos

## 🧪 Pasos para Probar

### Paso 1: Crear/Verificar Planes
```bash
cd arc_manager
python manage.py shell
```
```python
from apps.plans.models import Plan

# Verificar planes existentes
plans = Plan.objects.all()
for plan in plans:
    print(f"{plan.name}: ${plan.price} - {plan.display_name}")
```

### Paso 2: Asegurar Usuario de Prueba
```python
from apps.accounts.models import User
from apps.orgs.models import Organization

# Crear organización de prueba
org = Organization.objects.create(
    name="Empresa Test",
    slug="empresa-test",
    is_active=True
)

# Crear usuario admin de la organización
user = User.objects.create_user(
    email="admin@empresa-test.com",
    username="admin_test",
    password="test123",
    first_name="Admin",
    last_name="Test",
    is_org_admin=True
)
user.organization = org
user.save()
```

### Paso 3: Asignar Plan Inicial
```python
from apps.plans.models import Plan, Subscription

# Asignar plan trial/gratuito inicial
trial_plan = Plan.objects.filter(name='trial').first()
if trial_plan:
    subscription, created = Subscription.objects.get_or_create(
        organization=org,
        defaults={'plan': trial_plan}
    )
    print(f"Suscripción creada: {subscription}")
```

### Paso 4: Probar Solicitud de Upgrade

1. **Login como usuario:**
   ```
   http://localhost:8000/accounts/login/
   Email: admin@empresa-test.com
   Password: test123
   ```

2. **Ir al Dashboard:**
   ```
   http://localhost:8000/plans/dashboard/
   ```

3. **Solicitar Upgrade:**
   - Clic en "Solicitar Upgrade"
   - Seleccionar plan superior
   - Llenar datos de contacto
   - Enviar solicitud

### Paso 5: Probar Proceso de Aprobación

1. **Como Administrador Django:**
   ```
   http://localhost:8000/admin/
   ```

2. **Ir a Solicitudes de Upgrade:**
   ```
   Plans → Solicitudes de upgrade
   ```

3. **Aprobar Solicitud:**
   - Abrir la solicitud pendiente
   - Cambiar estado de "Pendiente" a "Aprobada - Pendiente de Pago"
   - Guardar cambios
   - **Verificar en consola:** Debe aparecer el email con instrucciones

### Paso 6: Simular Pago y Completar

1. **Anotar información de pago:**
   - En la misma solicitud
   - "Referencia de Pago": "TRANS20241201123456"
   - "Información del Comprobante": "Comprobante recibido por WhatsApp"

2. **Cambiar a "Pago Reportado":**
   - Estado: "Pago Reportado - En Verificación"
   - Guardar

3. **Completar Upgrade:**
   - Estado: "Completada"
   - Guardar cambios
   - **Verificar en consola:** Email de confirmación

### Paso 7: Verificar Resultado Final

```python
# En Django shell
from apps.orgs.models import Organization

org = Organization.objects.get(slug="empresa-test")
subscription = org.subscription

print(f"Plan actual: {subscription.plan.display_name}")
print(f"Estado: {subscription.status}")
print(f"Historial de pagos: {subscription.metadata.get('payment_history', [])}")
```

## 📋 Lista de Verificación

### ✅ Antes de Usar en Producción:

1. **Configurar Email SMTP:**
   ```python
   # En settings.py, cambiar:
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'tu-servidor-smtp'
   EMAIL_HOST_USER = 'tu-email@tudominio.com'
   EMAIL_HOST_PASSWORD = 'tu-contraseña'
   ```

2. **Actualizar Información Bancaria:**
   ```python
   PAYMENT_BANK_INFO = {
       'bank_name': 'Tu Banco Real',
       'account_holder': 'TU EMPRESA REAL SA DE CV',
       'account_number': 'CUENTA-REAL',
       'clabe': 'CLABE-REAL',
       'concept_prefix': 'ArcManager-Upgrade'
   }
   ```

3. **Configurar Dominio:**
   ```python
   SITE_URL = 'https://tudominio.com'
   DEFAULT_FROM_EMAIL = 'Tu Empresa <noreply@tudominio.com>'
   ```

## 🚨 Problemas Comunes y Soluciones

### "No veo la solicitud en el admin"
```bash
# Verificar si se creó
python manage.py shell
from apps.plans.models import UpgradeRequest
print(UpgradeRequest.objects.all())
```

### "El email no se envía"
- En desarrollo: Revisar la consola donde corre el servidor
- En producción: Verificar configuración SMTP en settings.py

### "El plan no se actualiza"
- Verificar que el estado cambió a "Completada"
- Verificar que la organización tiene una suscripción

### "Error al cambiar plan en admin de organizaciones"
- ✅ **Correcto**: Eso ahora está bloqueado intencionalmente
- ❌ **No hacer**: Cambiar planes de pago desde ahí
- ✅ **Usar**: Sistema de "Solicitudes de Upgrade"

## 🎯 Estados del Sistema

| Flujo | Usuario Ve | Admin Ve | Acción Requerida |
|-------|------------|----------|------------------|
| 1️⃣ Solicitud | "Solicitud enviada" | 🟠 Pendiente | Aprobar |
| 2️⃣ Aprobada | "Aprobada, pagar" | 🔵 Aprobada | Esperar pago |
| 3️⃣ Pagó | "Verificando pago" | 🟣 Pago reportado | Completar |
| 4️⃣ Final | "¡Plan activo!" | 🟢 Completada | ✅ Terminado |

---

**💡 Consejo:** Haz estas pruebas en este orden para asegurar que todo funciona antes de usar con clientes reales. 