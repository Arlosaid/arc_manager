/**
 * Plans JavaScript Optimizado - Arc Manager
 * Versión simplificada y eficiente
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
    setupAccessibility();
}

/**
 * Configura las barras de progreso con animación suave
 */
function setupProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    
    progressBars.forEach(progressBar => {
        const percentage = parseInt(progressBar.getAttribute('data-percentage')) || 0;
        
        // Animar progreso
        setTimeout(() => {
            progressBar.style.width = percentage + '%';
        }, 100);
        
        // Configurar colores según porcentaje
        updateProgressBarColor(progressBar, percentage);
    });
}

/**
 * Actualiza el color de la barra de progreso según el porcentaje
 */
function updateProgressBarColor(progressBar, percentage) {
    const colors = {
        danger: '#dc2626',
        warning: '#d97706',
        normal: '#2563eb'
    };
    
    if (percentage >= 90) {
        progressBar.style.background = colors.danger;
    } else if (percentage >= 70) {
        progressBar.style.background = colors.warning;
    } else {
        progressBar.style.background = colors.normal;
    }
}

/**
 * Configura las interacciones básicas
 */
function setupInteractions() {
    // Delegación de eventos para mejor rendimiento
    document.addEventListener('click', handleDocumentClick);
    document.addEventListener('mouseenter', handleMouseEnter, true);
    document.addEventListener('mouseleave', handleMouseLeave, true);
}

/**
 * Maneja clics en el documento usando delegación de eventos
 */
function handleDocumentClick(e) {
    const target = e.target;
    
    // Botones de upgrade
    if (target.matches('.upgrade-btn-cta, .plan-select-button')) {
        handleUpgradeClick(e);
    }
    
    // Enlaces de soporte
    if (target.matches('.support-contact')) {
        handleSupportClick(e);
    }
    
    // Botones de cierre de banner
    if (target.matches('.close-banner')) {
        closeBanner(e);
    }
}

/**
 * Maneja efectos hover
 */
function handleMouseEnter(e) {
    const target = e.target;
    
    if (target.matches('.usage-card, .plan-item, .payment-history-item')) {
        target.style.transform = 'translateY(-2px)';
    }
}

function handleMouseLeave(e) {
    const target = e.target;
    
    if (target.matches('.usage-card, .plan-item, .payment-history-item')) {
        target.style.transform = 'translateY(0)';
    }
}

/**
 * Maneja los clics en botones de upgrade
 */
function handleUpgradeClick(e) {
    const button = e.currentTarget;
    
    // Efecto visual
    button.style.transform = 'scale(0.98)';
    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 150);
    
    // Feedback visual
    showNotification('Redirigiendo a la página de upgrade...', 'info', 2000);
}

/**
 * Maneja los clics en enlaces de soporte
 */
function handleSupportClick(e) {
    const link = e.currentTarget;
    
    // Efecto visual
    link.style.transform = 'scale(1.05)';
    setTimeout(() => {
        link.style.transform = 'scale(1)';
    }, 200);
    
    showNotification('Abriendo enlace de soporte...', 'info', 2000);
}

/**
 * Cierra un banner
 */
function closeBanner(e) {
    const banner = e.currentTarget.closest('.notification-banner');
    if (banner) {
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            banner.remove();
        }, 300);
    }
}

/**
 * Configura el sistema de notificaciones
 */
function setupNotifications() {
    // Crear contenedor si no existe
    if (!document.getElementById('notifications-container')) {
        const container = document.createElement('div');
        container.id = 'notifications-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 350px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }
    
    // Agregar botones de cierre a banners existentes
    addCloseBtnsToBanners();
}

/**
 * Agrega botones de cierre a banners existentes
 */
function addCloseBtnsToBanners() {
    const banners = document.querySelectorAll('.notification-banner:not([data-closable])');
    
    banners.forEach(banner => {
        banner.setAttribute('data-closable', 'true');
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'close-banner';
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            opacity: 0.8;
            z-index: 10;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.2s ease;
        `;
        
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.opacity = '1';
            closeBtn.style.background = 'rgba(255, 255, 255, 0.3)';
        });
        
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.opacity = '0.8';
            closeBtn.style.background = 'rgba(255, 255, 255, 0.2)';
        });
        
        banner.style.position = 'relative';
        banner.appendChild(closeBtn);
    });
}

/**
 * Muestra una notificación
 */
function showNotification(message, type = 'info', duration = 4000) {
    const container = document.getElementById('notifications-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const colors = {
        info: '#2563eb',
        success: '#059669',
        warning: '#d97706',
        error: '#dc2626'
    };
    
    const icons = {
        info: 'fas fa-info-circle',
        success: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-triangle',
        error: 'fas fa-times-circle'
    };
    
    notification.style.cssText = `
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        position: relative;
        font-size: 0.875rem;
        pointer-events: auto;
        max-width: 100%;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="${icons[type]}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: white; font-size: 18px; cursor: pointer; margin-left: auto; padding: 0;">×</button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Animar entrada
    requestAnimationFrame(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    });
    
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
 * Configura mejoras de accesibilidad
 */
function setupAccessibility() {
    // Navegación por teclado
    document.addEventListener('keydown', handleKeyNavigation);
    
    // Mejorar focus visual
    const focusableElements = document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    focusableElements.forEach(element => {
        element.addEventListener('focus', () => {
            element.style.outline = '2px solid #2563eb';
            element.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', () => {
            element.style.outline = 'none';
        });
    });
}

/**
 * Maneja navegación por teclado
 */
function handleKeyNavigation(e) {
    // Cerrar notificaciones con Escape
    if (e.key === 'Escape') {
        const notifications = document.querySelectorAll('.notification');
        notifications.forEach(notification => {
            notification.remove();
        });
    }
    
    // Cerrar banners con Escape
    if (e.key === 'Escape' && e.target.closest('.notification-banner')) {
        const banner = e.target.closest('.notification-banner');
        const closeBtn = banner.querySelector('.close-banner');
        if (closeBtn) {
            closeBtn.click();
        }
    }
}

/**
 * Actualiza el valor de una métrica (utilidad)
 */
function updateMetricValue(metricId, value) {
    const element = document.querySelector(`[data-metric="${metricId}"]`);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Valida un formulario (utilidad)
 */
function validateForm(form) {
    return form.checkValidity();
}

/**
 * Maneja errores de carga de recursos
 */
function handleResourceError(error) {
    console.warn('Error cargando recurso:', error);
    showNotification('Error cargando algunos recursos. Por favor, recarga la página.', 'warning', 6000);
}

// Manejar errores de carga de imágenes
document.addEventListener('error', handleResourceError, true);

// Exportar funciones principales para uso global
window.PlansJS = {
    showNotification,
    updateMetricValue,
    setupProgressBars,
    validateForm
};

// Logging para desarrollo
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('Plans.js cargado correctamente');
}
