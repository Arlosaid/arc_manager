/**
 * ===== UPGRADE PLAN JAVASCRIPT - OPTIMIZADO =====
 * JavaScript optimizado para la funcionalidad de upgrade de planes
 */

// Configuración
const CONFIG = {
    DEBUG: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
    TIMEOUT: 10000 // 10 segundos
};

function debugLog(message, data = null) {
    if (CONFIG.DEBUG) {
        console.log(`[UpgradePlan] ${message}`, data || '');
    }
}

class UpgradePlanManager {
    constructor() {
        debugLog('Iniciando UpgradePlanManager');
        this.processingIndicator = null;
        this.init();
    }

    init() {
        debugLog('Inicializando componentes');
        this.setupUpgradeForms();
        this.setupModalFunctionality();
        this.enhanceNotifications();
        this.setupKeyboardNavigation();
        debugLog('Componentes inicializados');
    }

    /**
     * Configurar formularios de upgrade - VERSIÓN OPTIMIZADA
     */
    setupUpgradeForms() {
        const upgradeForms = document.querySelectorAll('form.upgrade-form');
        debugLog(`Formularios encontrados: ${upgradeForms.length}`);
        
        upgradeForms.forEach((form, index) => {
            debugLog(`Configurando formulario ${index + 1}`, form);
            
            form.addEventListener('submit', (e) => this.handleFormSubmit(e, form));
        });
    }

    /**
     * Maneja el envío de formularios de upgrade
     */
    handleFormSubmit(e, form) {
        debugLog('Formulario enviado - procesando', {
            action: form.action,
            method: form.method
        });
        
        // Validar formulario
        if (!this.validateForm(form)) {
            debugLog('ERROR: Formulario inválido');
            e.preventDefault();
            this.showError('Error: Formulario inválido. Por favor, recarga la página.');
            return false;
        }
        
        debugLog('Formulario válido, datos:', this.getFormData(form));
        
        // Mostrar estado de carga
        this.showLoadingState(form);
        
        // Permitir envío normal del formulario
        debugLog('Permitiendo envío normal del formulario');
        return true;
    }

    /**
     * Valida un formulario de upgrade
     */
    validateForm(form) {
        const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]');
        const requestedPlan = form.querySelector('[name="requested_plan"]');
        
        return csrfToken && requestedPlan && form.checkValidity();
    }

    /**
     * Obtiene los datos del formulario
     */
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }

    /**
     * Muestra estado de carga optimizado
     */
    showLoadingState(form) {
        debugLog('Mostrando estado de carga');
        
        const button = form.querySelector('.cta-button, button[type="submit"]');
        if (button) {
            this.disableButton(button);
        }
        
        this.showProcessingIndicator();
    }

    /**
     * Deshabilita un botón con estado de carga
     */
    disableButton(button) {
        debugLog('Deshabilitando botón de envío');
        
        button.disabled = true;
        const span = button.querySelector('span');
        const icon = button.querySelector('i');
        
        if (span) {
            span.setAttribute('data-original-text', span.textContent);
            span.textContent = 'Procesando...';
        }
        
        if (icon) {
            icon.setAttribute('data-original-class', icon.className);
            icon.className = 'fas fa-spinner fa-spin';
        }
    }

    /**
     * Muestra indicador de procesamiento optimizado
     */
    showProcessingIndicator() {
        // Remover indicador anterior
        this.hideProcessingIndicator();
        
        this.processingIndicator = document.createElement('div');
        this.processingIndicator.id = 'processing-indicator';
        this.processingIndicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #2563eb;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            z-index: 10000;
            font-weight: 500;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        this.processingIndicator.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            <span>Enviando solicitud...</span>
        `;
        
        document.body.appendChild(this.processingIndicator);
        
        // Animar entrada
        requestAnimationFrame(() => {
            this.processingIndicator.style.opacity = '1';
            this.processingIndicator.style.transform = 'translateX(0)';
        });
        
        // Auto-remover después del timeout
        setTimeout(() => {
            this.hideProcessingIndicator();
        }, CONFIG.TIMEOUT);
    }

    /**
     * Oculta el indicador de procesamiento
     */
    hideProcessingIndicator() {
        if (this.processingIndicator && this.processingIndicator.parentNode) {
            this.processingIndicator.style.opacity = '0';
            this.processingIndicator.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (this.processingIndicator && this.processingIndicator.parentNode) {
                    this.processingIndicator.parentNode.removeChild(this.processingIndicator);
                }
            }, 300);
        }
    }

    /**
     * Configura funcionalidad del modal
     */
    setupModalFunctionality() {
        debugLog('Configurando funcionalidad del modal');
        
        const modal = document.getElementById('upgradeConfirmModal');
        if (!modal) {
            debugLog('Modal no encontrado - skipping');
            return;
        }

        // Delegación de eventos para el modal
        modal.addEventListener('click', (e) => {
            if (e.target.matches('.btn-close-custom, .btn-cancel') || e.target === modal) {
                this.closeModal();
            }
        });
        
        debugLog('Modal configurado');
    }

    /**
     * Cierra el modal
     */
    closeModal() {
        debugLog('Cerrando modal');
        
        const modal = document.getElementById('upgradeConfirmModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('visible');
        }
        
        document.body.style.overflow = '';
        debugLog('Modal cerrado');
    }

    /**
     * Mejora notificaciones existentes
     */
    enhanceNotifications() {
        debugLog('Mejorando notificaciones');
        
        const messages = document.querySelectorAll('.alert');
        debugLog(`Notificaciones encontradas: ${messages.length}`);
        
        messages.forEach((message, index) => {
            debugLog(`Procesando notificación ${index + 1}`);
            this.enhanceMessage(message);
        });
    }

    /**
     * Mejora un mensaje individual
     */
    enhanceMessage(message) {
        // Agregar icono si no existe
        if (!message.querySelector('i')) {
            const icon = document.createElement('i');
            icon.className = this.getIconForMessageType(message);
            
            message.insertBefore(icon, message.firstChild);
            message.style.cssText += `
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                font-weight: 500;
            `;
        }
        
        // Agregar botón de cierre
        this.addCloseButton(message);
    }

    /**
     * Obtiene el icono apropiado para el tipo de mensaje
     */
    getIconForMessageType(message) {
        if (message.classList.contains('alert-success')) {
            return 'fas fa-check-circle';
        } else if (message.classList.contains('alert-info')) {
            return 'fas fa-info-circle';
        } else if (message.classList.contains('alert-warning')) {
            return 'fas fa-exclamation-triangle';
        } else if (message.classList.contains('alert-danger')) {
            return 'fas fa-times-circle';
        }
        return 'fas fa-info-circle';
    }

    /**
     * Agrega botón de cierre a un mensaje
     */
    addCloseButton(message) {
        if (message.querySelector('.close-btn')) return;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'close-btn';
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            margin-left: auto;
            opacity: 0.7;
            transition: opacity 0.2s ease;
        `;
        
        closeBtn.addEventListener('click', () => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                message.remove();
            }, 300);
        });
        
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.opacity = '1';
        });
        
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.opacity = '0.7';
        });
        
        message.appendChild(closeBtn);
    }

    /**
     * Configura navegación por teclado
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                
                // Cerrar mensajes
                const messages = document.querySelectorAll('.alert');
                messages.forEach(message => {
                    const closeBtn = message.querySelector('.close-btn');
                    if (closeBtn) {
                        closeBtn.click();
                    }
                });
            }
        });
    }

    /**
     * Restaura el estado original del formulario
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
        
        this.hideProcessingIndicator();
    }

    /**
     * Muestra un mensaje de error
     */
    showError(message) {
        if (window.PlansJS && window.PlansJS.showNotification) {
            window.PlansJS.showNotification(message, 'error', 6000);
        } else {
            alert(message);
        }
    }

    /**
     * Muestra un mensaje de éxito
     */
    showSuccess(message) {
        if (window.PlansJS && window.PlansJS.showNotification) {
            window.PlansJS.showNotification(message, 'success', 4000);
        } else {
            alert(message);
        }
    }
}

// Funciones globales para compatibilidad
window.handleUpgradeError = function(form) {
    debugLog('Manejando error de upgrade');
    if (window.upgradeManager) {
        window.upgradeManager.restoreFormState(form);
    }
};

// Inicialización
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