/**
 * ===== UPGRADE PLAN JAVASCRIPT - SIMPLIFICADO Y FUNCIONAL =====
 * JavaScript simplificado para la funcionalidad de upgrade de planes
 */

// Modo debug - cambiar a false en producción
const DEBUG_MODE = true;

function debugLog(message, data = null) {
    if (DEBUG_MODE) {
        console.log(`[UpgradePlan] ${message}`, data || '');
    }
}

class UpgradePlanManager {
    constructor() {
        debugLog('Iniciando UpgradePlanManager');
        this.init();
    }

    init() {
        debugLog('Inicializando componentes');
        this.setupUpgradeForms();
        this.setupModalFunctionality();
        this.enhanceNotifications();
        debugLog('Componentes inicializados');
    }

    /**
     * Configurar formularios de upgrade - VERSIÓN SIMPLIFICADA
     */
    setupUpgradeForms() {
        const upgradeForms = document.querySelectorAll('form.upgrade-form');
        debugLog(`Formularios encontrados: ${upgradeForms.length}`);
        
        upgradeForms.forEach((form, index) => {
            debugLog(`Configurando formulario ${index + 1}`, form);
            
            // Agregar listener de submit
            form.addEventListener('submit', (e) => {
                debugLog('Formulario enviado - procesando', {
                    action: form.action,
                    method: form.method
                });
                
                // Validar formulario
                const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]');
                const requestedPlan = form.querySelector('[name="requested_plan"]');
                
                if (!csrfToken || !requestedPlan) {
                    debugLog('ERROR: Formulario inválido', {
                        csrfToken: !!csrfToken,
                        requestedPlan: !!requestedPlan
                    });
                    e.preventDefault();
                    alert('Error: Formulario inválido. Por favor, recarga la página.');
                    return false;
                }
                
                debugLog('Formulario válido, datos:', {
                    csrfToken: csrfToken.value,
                    requestedPlan: requestedPlan.value
                });
                
                // Mostrar estado de carga
                this.showLoadingState(form);
                
                // Permitir envío normal del formulario
                debugLog('Permitiendo envío normal del formulario');
                return true;
            });
        });
    }

    /**
     * Mostrar estado de carga
     */
    showLoadingState(form) {
        debugLog('Mostrando estado de carga');
        
        const button = form.querySelector('.cta-button, button[type="submit"]');
        if (button) {
            debugLog('Deshabilitando botón de envío');
            button.disabled = true;
            const span = button.querySelector('span');
            const icon = button.querySelector('i');
            
            if (span) {
                const originalText = span.textContent;
                span.textContent = 'Procesando...';
                span.setAttribute('data-original-text', originalText);
            }
            if (icon) {
                const originalClass = icon.className;
                icon.className = 'fas fa-spinner fa-spin';
                icon.setAttribute('data-original-class', originalClass);
            }
        }
        
        // Mostrar indicador visual
        this.showProcessingIndicator();
    }

    /**
     * Mostrar indicador de procesamiento
     */
    showProcessingIndicator() {
        // Remover indicador anterior si existe
        const existingIndicator = document.getElementById('processing-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        const indicator = document.createElement('div');
        indicator.id = 'processing-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 10000;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        
        indicator.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            <span>Enviando solicitud...</span>
        `;
        
        document.body.appendChild(indicator);
        
        // Remover después de 10 segundos por si hay algún error
        setTimeout(() => {
            if (indicator && indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
        }, 10000);
    }

    /**
     * Configurar funcionalidad del modal (para referencias futuras)
     */
    setupModalFunctionality() {
        debugLog('Configurando funcionalidad del modal');
        
        const modal = document.getElementById('upgradeConfirmModal');
        if (!modal) {
            debugLog('Modal no encontrado - skipping');
            return;
        }

        // Botón de cierre
        const closeBtn = modal.querySelector('.btn-close-custom');
        if (closeBtn) {
            closeBtn.onclick = () => {
                debugLog('Botón de cierre clickeado');
                this.closeModal();
            };
        }

        // Botón cancelar
        const cancelBtn = modal.querySelector('.btn-cancel');
        if (cancelBtn) {
            cancelBtn.onclick = () => {
                debugLog('Botón cancelar clickeado');
                this.closeModal();
            };
        }

        // Cerrar con click en backdrop
        modal.onclick = (e) => {
            if (e.target === modal) {
                debugLog('Click en backdrop - cerrando modal');
                this.closeModal();
            }
        };
        
        debugLog('Modal configurado');
    }

    /**
     * Cerrar modal
     */
    closeModal() {
        debugLog('Cerrando modal');
        
        const modal = document.getElementById('upgradeConfirmModal');
        if (modal) {
            modal.style.display = 'none';
        }
        
        document.body.style.overflow = '';
        debugLog('Modal cerrado');
    }

    /**
     * Mejorar notificaciones existentes
     */
    enhanceNotifications() {
        debugLog('Mejorando notificaciones');
        
        const messages = document.querySelectorAll('.alert');
        debugLog(`Notificaciones encontradas: ${messages.length}`);
        
        messages.forEach((message, index) => {
            debugLog(`Procesando notificación ${index + 1}`);
            
            // Agregar icono si no existe
            if (!message.querySelector('i')) {
                const icon = document.createElement('i');
                
                if (message.classList.contains('alert-success')) {
                    icon.className = 'fas fa-check-circle';
                } else if (message.classList.contains('alert-info')) {
                    icon.className = 'fas fa-info-circle';
                } else if (message.classList.contains('alert-warning')) {
                    icon.className = 'fas fa-exclamation-triangle';
                } else if (message.classList.contains('alert-danger')) {
                    icon.className = 'fas fa-times-circle';
                }
                
                message.insertBefore(icon, message.firstChild);
                message.style.display = 'flex';
                message.style.alignItems = 'center';
                message.style.gap = '10px';
            }
        });
    }

    /**
     * Restaurar estado original del formulario (por si hay error)
     */
    restoreFormState(form) {
        debugLog('Restaurando estado del formulario');
        
        const button = form.querySelector('.cta-button, button[type="submit"]');
        if (button) {
            button.disabled = false;
            
            const span = button.querySelector('span');
            const icon = button.querySelector('i');
            
            if (span && span.getAttribute('data-original-text')) {
                span.textContent = span.getAttribute('data-original-text');
            }
            if (icon && icon.getAttribute('data-original-class')) {
                icon.className = icon.getAttribute('data-original-class');
            }
        }
        
        // Remover indicador de procesamiento
        const indicator = document.getElementById('processing-indicator');
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }
}

// Función global para manejo de errores
window.handleUpgradeError = function(form) {
    debugLog('Manejando error de upgrade');
    if (window.upgradeManager) {
        window.upgradeManager.restoreFormState(form);
    }
};

// Función para formularios simples (backup)
window.handleSimpleUpgrade = function(form) {
    debugLog('Manejando upgrade simple');
    const confirmed = confirm('¿Confirmas que quieres solicitar este upgrade?');
    if (confirmed) {
        debugLog('Upgrade confirmado - enviando formulario');
        return true;
    } else {
        debugLog('Upgrade cancelado');
        return false;
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    debugLog('DOM cargado - inicializando UpgradePlanManager');
    window.upgradeManager = new UpgradePlanManager();
});

// Backup: Inicializar si el DOM ya está listo
if (document.readyState === 'loading') {
    debugLog('DOM aún cargando - esperando DOMContentLoaded');
} else {
    debugLog('DOM ya cargado - inicializando UpgradePlanManager inmediatamente');
    window.upgradeManager = new UpgradePlanManager();
}