/**
 * ===== UPGRADE PLAN JAVASCRIPT - FUNCIONALIDAD INTERNA =====
 * Para la página de actualización de planes dentro de la aplicación
 */

class UpgradePlanManager {
    constructor() {
        this.currentPlan = null;
        this.availablePlans = [];
        
        this.init();
    }

    init() {
        this.setupUpgradeForms();
        this.setupPlanComparison();
        this.extractPlanData();
        this.setupNotifications();
    }

    /**
     * Configurar formularios de upgrade
     */
    setupUpgradeForms() {
        const upgradeForms = document.querySelectorAll('form[method="post"]');
        
        upgradeForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleUpgradeRequest(form);
            });
        });

        // Configurar botones de upgrade
        const upgradeButtons = document.querySelectorAll('.cta-button');
        upgradeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                if (button.type === 'submit') {
                    // Ya manejado por el form submit
                    return;
                }
                e.preventDefault();
                this.animateButtonClick(button);
            });
        });
    }

    /**
     * Manejar solicitud de upgrade
     */
    handleUpgradeRequest(form) {
        const planId = form.querySelector('input[name="requested_plan"]').value;
        const planCard = form.closest('.pricing-card');
        const planName = planCard.querySelector('.plan-name').textContent;
        const planPrice = planCard.querySelector('.price:not([style*="display: none"])').textContent;
        
        // Animar botón
        const button = form.querySelector('.cta-button');
        this.animateButtonClick(button);
        
        // Mostrar confirmación si hay modal
        const modal = document.getElementById('upgradeConfirmModal');
        if (modal) {
            try {
                this.showUpgradeConfirmation(planName, planPrice, form);
            } catch (error) {
                console.error('Error con modal, enviando directamente:', error);
                this.submitUpgradeForm(form);
            }
        } else {
            // Enviar directamente si no hay modal
            this.submitUpgradeForm(form);
        }
    }

    /**
     * Mostrar modal de confirmación SIMPLIFICADO - sin Bootstrap
     */
    showUpgradeConfirmation(planName, planPrice, form) {
        // OPCIÓN ALTERNATIVA: Si el modal falla, usar confirmación simple
        const useSimpleConfirmation = false; // Cambiar a true si sigue fallando
        
        if (useSimpleConfirmation) {
            const confirmed = confirm(`¿Confirmas el upgrade al plan ${planName} por ${planPrice}/mes?`);
            if (confirmed) {
                this.submitUpgradeForm(form);
            }
            return;
        }
        
        const modal = document.getElementById('upgradeConfirmModal');
        if (!modal) {
            // Fallback: usar confirmación simple si no hay modal
            const confirmed = confirm(`¿Confirmas el upgrade al plan ${planName} por ${planPrice}/mes?`);
            if (confirmed) {
                this.submitUpgradeForm(form);
            }
            return;
        }
        
        const planNameEl = document.getElementById('selectedPlanName');
        const additionalCostEl = document.getElementById('additionalCost');
        const confirmButton = document.getElementById('confirmUpgrade');
        
        // Actualizar contenido del modal
        if (planNameEl) planNameEl.textContent = planName;
        if (additionalCostEl) additionalCostEl.textContent = planPrice;
        
        // Limpiar event listeners anteriores del botón confirmar
        if (confirmButton) {
            const newButton = confirmButton.cloneNode(true);
            confirmButton.parentNode.replaceChild(newButton, confirmButton);
            
            // Agregar nuevo event listener para confirmar
            newButton.addEventListener('click', () => {
                this.submitUpgradeForm(form);
                this.closeModal();
            });
        }
        
        // Configurar botones de cierre
        this.setupModalCloseButtons();
        
        // Mostrar modal de forma directa
        this.openModal();
    }

    /**
     * Abrir modal de forma directa sin Bootstrap
     */
    openModal() {
        const modal = document.getElementById('upgradeConfirmModal');
        if (!modal) return;

        // Mostrar modal
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden'; // Prevenir scroll del body
        
        // Agregar clase show con delay para animación
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // Enfocar en el modal para accesibilidad
        modal.focus();
    }

    /**
     * Cerrar modal de forma directa
     */
    closeModal() {
        const modal = document.getElementById('upgradeConfirmModal');
        if (!modal) return;

        // Ocultar con animación
        modal.classList.remove('show');
        
        setTimeout(() => {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = ''; // Restaurar scroll del body
        }, 300); // Esperar a que termine la animación
    }

    /**
     * Configurar botones de cierre del modal
     */
    setupModalCloseButtons() {
        const modal = document.getElementById('upgradeConfirmModal');
        if (!modal) return;

        // Botón X de cierre
        const closeBtn = modal.querySelector('.btn-close-custom');
        if (closeBtn) {
            closeBtn.onclick = () => this.closeModal();
        }

        // Botón cancelar
        const cancelBtn = modal.querySelector('.btn-cancel');
        if (cancelBtn) {
            cancelBtn.onclick = () => this.closeModal();
        }

        // Cerrar al hacer clic en el backdrop
        modal.onclick = (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        };

        // Cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                this.closeModal();
            }
        });
    }

    /**
     * Enviar formulario de upgrade
     */
    submitUpgradeForm(form) {
        const button = form.querySelector('.cta-button');
        const originalText = button.querySelector('.button-text').textContent;
        
        // Mostrar estado de carga
        button.disabled = true;
        button.querySelector('.button-text').textContent = 'Procesando...';
        button.querySelector('i').className = 'fas fa-spinner fa-spin';
        
        // Enviar formulario
        form.submit();
    }

    /**
     * Animar click de botón - SIN ANIMACIONES
     */
    animateButtonClick(button) {
        // Sin animaciones - solo feedback visual simple
        button.style.opacity = '0.8';
        setTimeout(() => {
            button.style.opacity = '1';
        }, 100);
    }

    /**
     * Crear efecto ripple - ELIMINADO
     */
    createRippleEffect(element) {
        // Función eliminada - sin efectos ripple
    }

    /**
     * Configurar comparación de planes - SIN ANIMACIONES
     */
    setupPlanComparison() {
        const pricingCards = document.querySelectorAll('.pricing-card');
        
        pricingCards.forEach(card => {
            // Sin animaciones hover - solo estilos CSS
            // Los efectos hover se manejan solo con CSS
        });
    }

    /**
     * Animar hover de tarjetas - ELIMINADO
     */
    animateCardHover(card, isEntering) {
        // Función eliminada - sin animaciones de hover
    }

    /**
     * Extraer datos de planes disponibles
     */
    extractPlanData() {
        const pricingCards = document.querySelectorAll('.pricing-card[data-plan]');
        
        this.availablePlans = Array.from(pricingCards).map(card => {
            const planName = card.querySelector('.plan-name')?.textContent || '';
            const price = card.querySelector('.price:not([style*="display: none"])')?.textContent || '0';
            const features = Array.from(card.querySelectorAll('.feature-item span')).map(el => el.textContent);

            return {
                name: card.getAttribute('data-plan'),
                displayName: planName,
                price: price,
                features: features,
                element: card
            };
        });
    }

    /**
     * Configurar sistema de notificaciones
     */
    setupNotifications() {
        // Buscar mensajes de Django
        const messages = document.querySelectorAll('.alert');
        messages.forEach(message => {
            this.enhanceMessage(message);
        });
    }

    /**
     * Mejorar mensajes de Django
     */
    enhanceMessage(messageEl) {
        // Agregar icono si no existe
        if (!messageEl.querySelector('i')) {
            const icon = document.createElement('i');
            
            if (messageEl.classList.contains('alert-success')) {
                icon.className = 'fas fa-check-circle';
            } else if (messageEl.classList.contains('alert-info')) {
                icon.className = 'fas fa-info-circle';
            } else if (messageEl.classList.contains('alert-warning')) {
                icon.className = 'fas fa-exclamation-triangle';
            } else if (messageEl.classList.contains('alert-danger')) {
                icon.className = 'fas fa-times-circle';
            }
            
            messageEl.insertBefore(icon, messageEl.firstChild);
        }

        // Sin animaciones
    }

    /**
     * Mostrar notificación personalizada
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-custom`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            max-width: 500px;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    /**
     * Obtener icono para notificación
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            info: 'fa-info-circle',
            warning: 'fa-exclamation-triangle',
            danger: 'fa-times-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Efectos de fade - SIN ANIMACIONES
     */
    fadeOut(element, callback) {
        if (!element) return;
        element.style.opacity = '0';
        if (callback) callback();
    }

    fadeIn(element) {
        if (!element) return;
        element.style.opacity = '1';
    }

    /**
     * Limpiar recursos
     */
    destroy() {
        // Limpiar event listeners si es necesario
        const forms = document.querySelectorAll('form[method="post"]');
        forms.forEach(form => {
            form.removeEventListener('submit', this.handleUpgradeRequest);
        });
    }
}

/**
 * Utilidades para la página de upgrade
 */
class UpgradeUtils {
    static formatPrice(price) {
        return Math.floor(price);
    }

    static animateValue(element, start, end, duration = 1000) {
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = start + (end - start) * easeOut;
            
            element.textContent = Math.floor(current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    static validateUpgradeRequest(currentPlan, targetPlan) {
        // Validar que es un upgrade válido
        if (!currentPlan || !targetPlan) {
            return { valid: false, message: 'Planes no válidos' };
        }

        if (targetPlan.price <= currentPlan.price) {
            return { valid: false, message: 'Solo puedes hacer upgrade a un plan superior' };
        }

        return { valid: true, message: 'Upgrade válido' };
    }
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar manager principal
    window.upgradePlanManager = new UpgradePlanManager();
    
    // Agregar estilos para las animaciones
    const style = document.createElement('style');
    style.textContent = `
        /* Animaciones eliminadas */
        
        .notification-custom {
            border-left: 4px solid var(--upgrade-primary, #4285f4);
        }
        
        .notification-custom .btn-close {
            background: none;
            border: none;
            font-size: 1.2em;
            opacity: 0.6;
            cursor: pointer;
        }
        
        .notification-custom .btn-close:hover {
            opacity: 1;
        }
        
        /* Animaciones fadeIn eliminadas */
        
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    `;
    document.head.appendChild(style);
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', () => {
    if (window.upgradePlanManager) {
        window.upgradePlanManager.destroy();
    }
});

// Exportar para uso global
window.UpgradePlanManager = UpgradePlanManager;
window.UpgradeUtils = UpgradeUtils;