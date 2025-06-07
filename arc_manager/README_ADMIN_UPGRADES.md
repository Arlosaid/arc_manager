# 📋 Guía del Administrador - Sistema de Upgrades

## 🚨 IMPORTANTE: Cómo Funciona el Sistema

### ❌ LO QUE NO DEBES HACER
- **NUNCA** cambiar planes de pago directamente desde el admin de Organizaciones
- **NUNCA** asignar planes Premium/Pro/Básico desde "Gestión de Plan" de organizaciones
- Eso solo es para planes gratuitos y de prueba

### ✅ FLUJO CORRECTO DE UPGRADES

#### 1. Usuario Solicita Upgrade
- El usuario va a su dashboard y hace clic en "Solicitar Upgrade"
- Llena el formulario y envía la solicitud
- Se crea un registro en "Solicitudes de Upgrade" con estado **Pendiente**

#### 2. Tú Apruebas la Solicitud
**Opción A - Individual:**
1. Ve a `Admin → Plans → Solicitudes de Upgrade`
2. Abre la solicitud específica
3. Cambia el estado de **"Pendiente de Aprobación"** a **"Aprobada - Pendiente de Pago"**
4. Guarda los cambios
5. ✅ Se envía automáticamente el email con instrucciones de pago

**Opción B - Masiva:**
1. Ve a `Admin → Plans → Solicitudes de Upgrade`
2. Selecciona las solicitudes pendientes
3. Usa la acción: "✅ Aprobar solicitudes seleccionadas"
4. ✅ Se envían emails a todos automáticamente

#### 3. Cliente Realiza el Pago
- El cliente recibe el email con datos bancarios
- Hace la transferencia
- Envía comprobante por email o WhatsApp
- (Opcional) Puede reportar el pago en su dashboard

#### 4. Tú Verificas el Pago
**Cuando recibas el comprobante:**
1. Ve a la solicitud específica
2. En "Información de Pago" anota:
   - **Referencia de Pago**: Número de transferencia
   - **Información del Comprobante**: "Comprobante recibido por email/WhatsApp"
3. Cambia el estado a **"Pago Reportado - En Verificación"**
4. Guarda los cambios

#### 5. Activas el Nuevo Plan
**Después de verificar el comprobante:**
1. Cambia el estado a **"Completada"**
2. Guarda los cambios
3. ✅ El sistema automáticamente:
   - Cambia el plan de la organización
   - Actualiza las fechas de suscripción
   - Envía email de confirmación al cliente
   - Registra el pago en el historial

## 🎛️ Estados Explicados

| Estado | Color | Qué Significa | Acción Necesaria |
|--------|-------|---------------|-------------------|
| 🟠 **Pendiente** | Naranja | Nueva solicitud | ➡️ Cambiar a "Aprobada" |
| 🔵 **Aprobada** | Azul | Email enviado, esperando pago | ⏳ Esperar comprobante del cliente |
| 🟣 **Pago Reportado** | Morado | Cliente envió comprobante | ✅ Verificar y cambiar a "Completada" |
| 🟢 **Completada** | Verde | Plan activado exitosamente | ✨ Proceso terminado |
| 🔴 **Rechazada** | Rojo | Solicitud denegada | ❌ Proceso terminado |

## 🔧 Herramientas Disponibles

### En el Admin de Solicitudes de Upgrade:
- **Lista**: Ve todas las solicitudes con colores por estado
- **Filtros**: Por estado, fecha, plan, organización
- **Acciones masivas**: Aprobar, rechazar, marcar pagos en lote
- **Vista individual**: Cambio de estado con guías contextuales

### En el Admin de Organizaciones:
- **Plan Actual**: Solo muestra planes gratuitos/trial
- **Información de Suscripción**: Estado y días restantes
- **Enlaces directos**: A la suscripción y solicitudes de upgrade

## 📧 Emails Automáticos

### Cuando Apruebas (Estado: Aprobada)
```
✅ Solicitud de Upgrade Aprobada - Plan Premium

¡Hola!
Tu solicitud de upgrade ha sido APROBADA 🎉

INFORMACIÓN PARA EL PAGO:
• Banco: [Tu banco]
• Beneficiario: [Tu empresa]
• Cuenta: [Número de cuenta]
• CLABE: [Tu CLABE]
• Concepto: Upgrade Plan - [organizacion]
• Monto: $XXX MXN

PRÓXIMOS PASOS:
1. Realiza la transferencia bancaria
2. Guarda tu comprobante de pago
3. Envíanos el comprobante por email/WhatsApp
4. Activaremos tu plan en máximo 24 horas
```

### Cuando Completas (Estado: Completada)
```
🎉 ¡Upgrade Completado! - Plan Premium

¡Felicidades! 🎉
Tu upgrade ha sido completado exitosamente.

• Plan anterior: Básico ($299/mes)
• Plan nuevo: Premium ($499/mes)
• Estado: ACTIVO ✅

Ya puedes disfrutar de todas las características de tu nuevo plan.
```

## ⚡ Comandos Rápidos

### Para aprobar rápidamente:
1. `Admin → Plans → Solicitudes de Upgrade`
2. Filtrar por "Pendiente de Aprobación"
3. Seleccionar todas → "Aprobar solicitudes seleccionadas"

### Para completar upgrades:
1. Filtrar por "Pago Reportado - En Verificación"
2. Abrir cada solicitud individualmente
3. Verificar comprobante
4. Cambiar estado a "Completada"

## 🚨 Solución de Problemas

### "No puedo cambiar el plan"
- ✅ **Correcto**: Usar "Solicitudes de Upgrade"
- ❌ **Incorrecto**: Cambiar desde admin de organizaciones

### "El email no se envía"
- Verifica la configuración de email en settings
- Revisa los logs del servidor
- Usa las acciones masivas si la individual falla

### "El plan no se actualiza"
- Asegúrate de cambiar el estado a "Completada"
- Verifica que la solicitud tenga estado "Pago Reportado" antes
- Revisa que la organización tenga una suscripción activa

## 📞 Configuración de Pago

### En settings.py agregar:
```python
PAYMENT_BANK_INFO = {
    'bank_name': 'Tu Banco',
    'account_holder': 'Tu Empresa SA de CV',
    'account_number': 'XXXX-XXXX-XXXX-1234',
    'clabe': '012345678901234567',
    'concept': 'Upgrade Plan'
}
```

---

**💡 Recuerda**: El flujo manual te da control total sobre los pagos y evita upgrades no autorizados. Los usuarios entienden que es un proceso manual y están dispuestos a esperar la verificación. 