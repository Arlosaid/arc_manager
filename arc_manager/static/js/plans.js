/**
 * Plans JavaScript Optimizado - Arc Manager
 * Versión simplificada con funcionalidad esencial
 */

document.addEventListener('DOMContentLoaded', function() {
    initializePlans();
});

/**
 * Inicializa toda la funcionalidad de planes
 */
function initializePlans() {
    setupProgressBars();
    setupInteractions();
    setupNotifications();
    setupForms();
}

/**
 * Configura las barras de progreso
 */
function setupProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    
    progressBars.forEach(progressBar => {
        const percentage = parseInt(progressBar.getAttribute('data-percentage')) || 0;
        
        // Configurar ancho final
        progressBar.style.width = percentage + '%';
        
        // Cambiar color según el porcentaje
        if (percentage >= 90) {
            progressBar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
        } else if (percentage >= 70) {
            progressBar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
        } else {
            progressBar.style.background = 'linear-gradient(90deg, #3b82f6, #60a5fa)';
        }
        
        // Actualizar texto del porcentaje
        const percentageElement = progressBar.parentElement.querySelector('.usage-percentage');
        if (percentageElement) {
            percentageElement.textContent = percentage + '%';
        }
    });
}

/**
 * Configura las interacciones básicas
 */
function setupInteractions() {
    // Botones de selección de plan
    const planButtons = document.querySelectorAll('.plan-select-button');
    planButtons.forEach(button => {
        button.addEventListener('click', handlePlanSelection);
    });
    
    // Botones de upgrade
    const upgradeButtons = document.querySelectorAll('.upgrade-btn-cta');
    upgradeButtons.forEach(button => {
        button.addEventListener('click', handleUpgradeClick);
    });
    
    // Enlaces de soporte
    const supportLinks = document.querySelectorAll('.support-contact');
    supportLinks.forEach(link => {
        link.addEventListener('click', handleSupportClick);
    });
    
    // Tarjetas con hover
    const cards = document.querySelectorAll('.usage-card, .plans-available-card, .payment-history-item');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
        });
    });
}

/**
 * Maneja la selección de plan
 */
function handlePlanSelection(e) {
    const button = e.currentTarget;
    const planType = button.getAttribute('data-plan') || 'basic';
    
    // Mostrar confirmación
    showConfirmationDialog(
        'Seleccionar Plan',
        `¿Estás seguro de que quieres seleccionar el plan ${planType}?`,
        () => {
            // Mostrar estado de carga
            const originalText = button.textContent;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            button.disabled = true;
            
            // Simular procesamiento
            setTimeout(() => {
                window.location.href = `/plans/request-upgrade/`;
            }, 1000);
        }
    );
}

/**
 * Maneja los clics en botones de upgrade
 */
function handleUpgradeClick(e) {
    const button = e.currentTarget;
    
    // Efecto visual simple
    button.style.transform = 'scale(0.98)';
    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 100);
    
    showNotification('Redirigiendo a la página de upgrade...', 'info');
}

/**
 * Maneja los clics en enlaces de soporte
 */
function handleSupportClick(e) {
    const link = e.currentTarget;
    
    showNotification('Abriendo enlace de soporte...', 'info');
    
    // Efecto visual
    link.style.transform = 'scale(1.05)';
    setTimeout(() => {
        link.style.transform = 'scale(1)';
    }, 200);
}

/**
 * Configura las notificaciones
 */
function setupNotifications() {
    // Crear contenedor de notificaciones
    if (!document.querySelector('.notifications-container')) {
        const container = document.createElement('div');
        container.className = 'notifications-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 350px;
        `;
        document.body.appendChild(container);
    }
    
    // Agregar botones de cerrar a banners existentes
    const banners = document.querySelectorAll('.notification-banner');
    banners.forEach(banner => {
        addCloseBanner(banner);
    });
}

/**
 * Agrega botón de cerrar a un banner
 */
function addCloseBanner(banner) {
    if (banner.querySelector('.close-banner')) return;
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-banner';
    closeBtn.innerHTML = '×';
    closeBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 15px;
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        opacity: 0.7;
        z-index: 10;
    `;
    
    closeBtn.addEventListener('click', () => {
        banner.style.display = 'none';
    });
    
    banner.style.position = 'relative';
    banner.appendChild(closeBtn);
}

/**
 * Configura los formularios
 */
function setupForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

/**
 * Maneja el envío de formularios
 */
function handleFormSubmit(e) {
    const form = e.currentTarget;
    const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
    
    if (submitButton) {
        const originalText = submitButton.textContent;
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        
        // Restaurar en caso de error
        setTimeout(() => {
            if (form.checkValidity()) {
                showNotification('Formulario enviado correctamente', 'success');
            } else {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
                showNotification('Por favor, revisa los datos del formulario', 'error');
                e.preventDefault();
            }
        }, 500);
    }
}

/**
 * Muestra una notificación
 */
function showNotification(message, type = 'info', duration = 4000) {
    const container = document.querySelector('.notifications-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const colors = {
        info: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    
    notification.style.cssText = `
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        position: relative;
        font-size: 0.875rem;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: white; font-size: 18px; cursor: pointer; margin-left: auto;">×</button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto-dismiss
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, duration);
}

/**
 * Muestra un diálogo de confirmación
 */
function showConfirmationDialog(title, message, onConfirm) {
    const overlay = document.createElement('div');
    overlay.className = 'confirmation-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    const dialog = document.createElement('div');
    dialog.className = 'confirmation-dialog';
    dialog.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        transform: scale(0.9);
        transition: transform 0.3s ease;
    `;
    
    dialog.innerHTML = `
        <h3 style="margin: 0 0 1rem 0; color: #1f2937; font-size: 1.25rem; font-weight: 600;">${title}</h3>
        <p style="margin: 0 0 2rem 0; color: #6b7280; line-height: 1.6;">${message}</p>
        <div style="display: flex; gap: 1rem; justify-content: flex-end;">
            <button class="cancel-btn" style="
                padding: 0.5rem 1rem;
                border: 1px solid #d1d5db;
                background: white;
                color: #6b7280;
                border-radius: 0.5rem;
                cursor: pointer;
                transition: all 0.2s ease;
            ">Cancelar</button>
            <button class="confirm-btn" style="
                padding: 0.5rem 1rem;
                border: none;
                background: #3b82f6;
                color: white;
                border-radius: 0.5rem;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s ease;
            ">Confirmar</button>
        </div>
    `;
    
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    
    // Animar entrada
    setTimeout(() => {
        overlay.style.opacity = '1';
        dialog.style.transform = 'scale(1)';
    }, 10);
    
    // Event listeners
    const cancelBtn = dialog.querySelector('.cancel-btn');
    const confirmBtn = dialog.querySelector('.confirm-btn');
    
    cancelBtn.addEventListener('click', () => {
        closeDialog(overlay);
    });
    
    confirmBtn.addEventListener('click', () => {
        closeDialog(overlay);
        onConfirm();
    });
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeDialog(overlay);
        }
    });
    
    // Hover effects
    cancelBtn.addEventListener('mouseenter', () => {
        cancelBtn.style.background = '#f3f4f6';
    });
    
    cancelBtn.addEventListener('mouseleave', () => {
        cancelBtn.style.background = 'white';
    });
    
    confirmBtn.addEventListener('mouseenter', () => {
        confirmBtn.style.background = '#2563eb';
    });
    
    confirmBtn.addEventListener('mouseleave', () => {
        confirmBtn.style.background = '#3b82f6';
    });
}

/**
 * Cierra un diálogo
 */
function closeDialog(overlay) {
    overlay.style.opacity = '0';
    const dialog = overlay.querySelector('.confirmation-dialog');
    dialog.style.transform = 'scale(0.9)';
    
    setTimeout(() => {
        overlay.remove();
    }, 300);
}

/**
 * Actualiza el valor de una métrica
 */
function updateMetricValue(metricId, value) {
    const element = document.querySelector(`[data-metric="${metricId}"]`);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Valida un formulario
 */
function validateForm(form) {
    return form.checkValidity();
}

// Exportar funciones principales
window.PlansJS = {
    showNotification,
    showConfirmationDialog,
    updateMetricValue,
    setupProgressBars
};
