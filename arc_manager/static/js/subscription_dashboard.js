// ===== SUBSCRIPTION_DASHBOARD.JS - LÓGICA PARA DASHBOARD DE SUSCRIPCIÓN =====

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    initializeTrialCountdown();
    initializeUsageAnimations();
});

function initializeDashboard() {
    // Actualizar cuenta regresiva del trial
    updateTrialCountdown();
    
    // Configurar animaciones de barras de progreso
    animateUsageBars();
    
    // Animar contador de días del trial
    animateTrialDaysCounter();
    
    // Configurar tooltips
    setupTooltips();
    
    // Verificar límites de uso
    checkUsageLimits();
    
    // Configurar actualizaciones automáticas
    setupAutoRefresh();
}

function initializeTrialCountdown() {
    const countdownElements = document.querySelectorAll('.trial-countdown');
    
    countdownElements.forEach(element => {
        const daysElement = element.querySelector('.countdown-circle span');
        if (daysElement) {
            const days = parseInt(daysElement.textContent);
            const totalDays = 30; // Asumiendo 30 días de trial
            const progressPercentage = ((totalDays - days) / totalDays) * 100;
            const progressDegrees = (progressPercentage / 100) * 360;
            
            // Actualizar el progreso circular
            const circle = element.querySelector('.countdown-circle');
            circle.style.setProperty('--progress-degrees', `${progressDegrees}deg`);
            
            // Agregar animación
            setTimeout(() => {
                circle.style.transition = 'background 1s ease-in-out';
            }, 100);
        }
    });
}

function initializeUsageAnimations() {
    // Animar barras de progreso enhanced
    const progressBarsEnhanced = document.querySelectorAll('.progress-fill-enhanced');
    progressBarsEnhanced.forEach((bar, index) => {
        const targetWidth = bar.getAttribute('data-width');
        if (targetWidth) {
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = targetWidth + '%';
            }, 300 + (index * 150));
        }
    });
    
    // Animar barras de progreso legacy
    const usageItems = document.querySelectorAll('.usage-item');
    usageItems.forEach((item, index) => {
        // Animar las barras de progreso
        const progressBar = item.querySelector('.usage-progress');
        if (progressBar) {
            const width = progressBar.style.width;
            progressBar.style.width = '0%';
            
            setTimeout(() => {
                progressBar.style.width = width;
            }, 300 + (index * 150));
        }
        
        // Agregar efecto hover mejorado
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Animar métricas enhanced
    const metricCards = document.querySelectorAll('.metric-card-enhanced');
    metricCards.forEach((card, index) => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// ===== MODAL DE CANCELACIÓN =====
function showCancelModal() {
    const modal = document.getElementById('cancelModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Agregar listener para cerrar con ESC
        document.addEventListener('keydown', handleModalEsc);
        
        // Agregar listener para cerrar clickeando fuera
        modal.addEventListener('click', handleModalOutsideClick);
    }
}

function hideCancelModal() {
    const modal = document.getElementById('cancelModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        
        // Remover listeners
        document.removeEventListener('keydown', handleModalEsc);
        modal.removeEventListener('click', handleModalOutsideClick);
    }
}

function handleModalEsc(e) {
    if (e.key === 'Escape') {
        hideCancelModal();
    }
}

function handleModalOutsideClick(e) {
    if (e.target === e.currentTarget) {
        hideCancelModal();
    }
}

function confirmCancel() {
    const cancelButton = document.querySelector('.btn-danger');
    
    // Mostrar estado de carga
    cancelButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    cancelButton.disabled = true;
    
    // Simular procesamiento (reemplaza con lógica real)
    setTimeout(() => {
        // Aquí irían las llamadas AJAX reales
        showNotification('Tu suscripción se pausará al final del período actual', 'success');
        hideCancelModal();
        
        // Actualizar estado en la página
        updateSubscriptionStatus('cancelled');
    }, 2000);
}

// ===== CUENTA REGRESIVA DEL TRIAL =====
function updateTrialCountdown() {
    const countdownElements = document.querySelectorAll('.countdown');
    
    countdownElements.forEach(element => {
        const text = element.textContent;
        const daysMatch = text.match(/(\d+) días/);
        
        if (daysMatch) {
            const days = parseInt(daysMatch[1]);
            
            // Cambiar color según días restantes
            if (days <= 3) {
                element.style.color = 'var(--arc-color-danger)';
                element.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${days} días`;
            } else if (days <= 7) {
                element.style.color = 'var(--arc-color-warning)';
                element.innerHTML = `<i class="fas fa-clock"></i> ${days} días`;
            }
            
            // Agregar pulsación si quedan pocos días
            if (days <= 5) {
                element.classList.add('pulse-warning');
            }
        }
    });
}

// ===== ANIMACIONES DE BARRAS DE PROGRESO =====
function animateUsageBars() {
    const progressBars = document.querySelectorAll('.usage-progress');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        // Animar después de un pequeño delay
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 300);
    });
}

// ===== ANIMACIÓN DE CONTADOR DE DÍAS =====
function animateTrialDaysCounter() {
    console.log('Iniciando animación de contador de días...');
    
    // Probar varios selectores posibles
    let trialDaysElement = document.querySelector('.trial-alert .trial-days');
    console.log('Selector 1 (.trial-alert .trial-days):', trialDaysElement);
    
    if (!trialDaysElement) {
        trialDaysElement = document.querySelector('.trial-days');
        console.log('Selector 2 (.trial-days):', trialDaysElement);
    }
    
    if (!trialDaysElement) {
        trialDaysElement = document.querySelector('.trial-countdown .trial-days');
        console.log('Selector 3 (.trial-countdown .trial-days):', trialDaysElement);
    }
    
    // Mostrar todos los elementos trial-alert y trial-days disponibles
    console.log('Todos los .trial-alert:', document.querySelectorAll('.trial-alert'));
    console.log('Todos los .trial-days:', document.querySelectorAll('.trial-days'));
    console.log('Todos los .trial-countdown:', document.querySelectorAll('.trial-countdown'));
    
    console.log('Elemento encontrado:', trialDaysElement);
    if (!trialDaysElement) return;
    
    // Obtener el número final desde el contenido del elemento (extraer solo número)
    const originalText = trialDaysElement.textContent;
    console.log('Texto original:', originalText);
    const numberMatch = originalText.match(/\d+/);
    if (!numberMatch) return;
    
    const finalNumber = parseInt(numberMatch[0]);
    console.log('Número final:', finalNumber);
    if (isNaN(finalNumber)) return;
    
    // Guardar el texto sin el número para reconstruirlo
    const textWithoutNumber = originalText.replace(/\d+/, '{NUMBER}');
    console.log('Plantilla de texto:', textWithoutNumber);
    
    // Configuración de la animación
    const duration = 1000; // 1 segundo
    const startNumber = 0;
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Usar una función de easing para suavizar la animación
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const currentNumber = Math.floor(easeOutCubic * finalNumber);
        
        // Reconstruir el texto con el número animado
        trialDaysElement.textContent = textWithoutNumber.replace('{NUMBER}', currentNumber);
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            // Asegurar que termine con el número correcto
            trialDaysElement.textContent = originalText;
            console.log('Animación completada');
        }
    }
    
    // Comenzar la animación
    requestAnimationFrame(updateCounter);
}

// ===== VERIFICACIÓN DE LÍMITES =====
function checkUsageLimits() {
    const usageItems = document.querySelectorAll('.usage-item');
    
    usageItems.forEach(item => {
        const progressBar = item.querySelector('.usage-progress');
        const statusElement = item.querySelector('.usage-status');
        
        if (progressBar) {
            const width = parseFloat(progressBar.style.width);
            
            // Actualizar colores según porcentaje
            if (width >= 100) {
                progressBar.style.background = 'linear-gradient(135deg, var(--arc-color-danger), #dc2626)';
                statusElement.classList.add('status-warning');
                item.classList.add('limit-reached');
            } else if (width >= 80) {
                progressBar.style.background = 'linear-gradient(135deg, var(--arc-color-warning), #d97706)';
                statusElement.classList.add('status-warning');
                item.classList.add('approaching-limit');
            }
        }
    });
}

// ===== TOOLTIPS =====
function setupTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const title = e.target.getAttribute('title');
    if (!title) return;
    
    // Crear tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = title;
    tooltip.style.cssText = `
        position: absolute;
        background: var(--arc-text-primary);
        color: white;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        z-index: 1000;
        max-width: 200px;
        word-wrap: break-word;
        box-shadow: var(--arc-shadow-md);
    `;
    
    document.body.appendChild(tooltip);
    
    // Posicionar tooltip
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    
    // Guardar referencia para limpieza
    e.target._tooltip = tooltip;
    
    // Remover title temporalmente para evitar tooltip nativo
    e.target._originalTitle = title;
    e.target.removeAttribute('title');
}

function hideTooltip(e) {
    if (e.target._tooltip) {
        document.body.removeChild(e.target._tooltip);
        delete e.target._tooltip;
    }
    
    // Restaurar title
    if (e.target._originalTitle) {
        e.target.setAttribute('title', e.target._originalTitle);
        delete e.target._originalTitle;
    }
}

// ===== NOTIFICACIONES =====
function showNotification(message, type = 'info') {
    // Remover notificaciones existentes
    const existingNotifications = document.querySelectorAll('.dashboard-notification');
    existingNotifications.forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `dashboard-notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: var(--arc-border-radius-sm);
        box-shadow: var(--arc-shadow-lg);
        border-left: 4px solid ${getNotificationColor(type)};
        padding: 1rem;
        max-width: 400px;
        z-index: 1001;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-times-circle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

function getNotificationColor(type) {
    const colors = {
        success: 'var(--arc-color-success)',
        warning: 'var(--arc-color-warning)',
        error: 'var(--arc-color-danger)',
        info: 'var(--arc-color-info)'
    };
    return colors[type] || colors.info;
}

// ===== ACTUALIZACIÓN DE ESTADO =====
function updateSubscriptionStatus(newStatus) {
    const statusBadge = document.querySelector('.status-badge');
    const cardFooter = document.querySelector('.subscription-card .card-footer');
    
    if (statusBadge && cardFooter) {
        // Actualizar badge
        statusBadge.className = `status-badge ${newStatus}`;
        
        // Actualizar contenido según estado
        switch (newStatus) {
            case 'cancelled':
                statusBadge.innerHTML = '<i class="fas fa-pause"></i> Pausada';
                cardFooter.innerHTML = `
                    <a href="/plans/request-upgrade/" class="btn-primary reactivate-btn">
                        <i class="fas fa-refresh"></i>
                        Reactivar Suscripción
                    </a>
                `;
                break;
        }
    }
}

// ===== AUTO-REFRESH =====
function setupAutoRefresh() {
    // Actualizar datos cada 5 minutos (solo si la página está visible)
    setInterval(() => {
        if (!document.hidden) {
            refreshUsageData();
        }
    }, 5 * 60 * 1000);
}

function refreshUsageData() {
    // Aquí iría la lógica para actualizar datos vía AJAX
    console.log('Actualizando datos de uso...');
    
    // Ejemplo de cómo sería una actualización real:
    /*
    fetch('/api/usage-data/')
        .then(response => response.json())
        .then(data => {
            updateUsageDisplay(data);
        })
        .catch(error => {
            console.error('Error actualizando datos:', error);
        });
    */
}

function updateUsageDisplay(data) {
    // Actualizar barras de progreso con nuevos datos
    if (data.users) {
        updateUsageBar('users', data.users.current, data.users.limit);
    }
    if (data.projects) {
        updateUsageBar('projects', data.projects.current, data.projects.limit);
    }
    if (data.storage) {
        updateUsageBar('storage', data.storage.current, data.storage.limit);
    }
}

function updateUsageBar(type, current, limit) {
    const percentage = Math.min((current / limit) * 100, 100);
    const usageItem = document.querySelector(`[data-usage-type="${type}"]`);
    
    if (usageItem) {
        const progressBar = usageItem.querySelector('.usage-progress');
        const numbers = usageItem.querySelector('.usage-numbers');
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
        
        if (numbers) {
            numbers.textContent = `${current} / ${limit}`;
        }
    }
}

// ===== UTILIDADES =====
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function calculateDaysUntil(dateString) {
    const targetDate = new Date(dateString);
    const today = new Date();
    const timeDiff = targetDate.getTime() - today.getTime();
    const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
    
    return Math.max(0, daysDiff);
}

// ===== MANEJO DE ERRORES =====
window.addEventListener('error', function(e) {
    console.error('Error en subscription_dashboard.js:', e.error);
    showNotification('Ha ocurrido un error inesperado', 'error');
});

// ===== ESTILOS DINÁMICOS =====
const dynamicStyles = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    @keyframes pulse-warning {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .pulse-warning {
        animation: pulse-warning 2s infinite;
    }
    
    .limit-reached {
        background: rgba(239, 68, 68, 0.05) !important;
        border-color: var(--arc-color-danger) !important;
    }
    
    .approaching-limit {
        background: rgba(245, 158, 11, 0.05) !important;
        border-color: var(--arc-color-warning) !important;
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex: 1;
    }
    
    .notification-close {
        background: none;
        border: none;
        cursor: pointer;
        color: var(--arc-text-secondary);
        padding: 0.25rem;
    }
    
    .notification-close:hover {
        color: var(--arc-text-primary);
    }
`;

// Agregar estilos dinámicos
const styleSheet = document.createElement('style');
styleSheet.textContent = dynamicStyles;
document.head.appendChild(styleSheet);

// ===== EXPORTAR FUNCIONES PÚBLICAS =====
window.SubscriptionDashboard = {
    showCancelModal,
    hideCancelModal,
    confirmCancel,
    showNotification,
    refreshUsageData,
    updateSubscriptionStatus
}; 