/**
 * ===== PLANS.JS - FUNCIONALIDAD SIMPLIFICADA PARA DASHBOARD DE SUSCRIPCIONES =====
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeSubscriptionDashboard();
});

/**
 * Inicializa toda la funcionalidad del dashboard de suscripciones
 */
function initializeSubscriptionDashboard() {
    initializeProgressBars();
    initializeUsageCounters();
    initializePlanOptions();
    initializeTrialCountdown();
    initializeAnimations();
}

/**
 * Inicializa las barras de progreso con animaciones
 */
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    
    progressBars.forEach((progressBar, index) => {
        const percentage = parseInt(progressBar.getAttribute('data-percentage')) || 0;
        
        // Establecer el ancho inicial en 0
        progressBar.style.width = '0%';
        
        // Aplicar animación con delay escalonado
        setTimeout(() => {
            animateProgressBar(progressBar, percentage);
        }, (index * 200) + 500);
        
        // Cambiar color basado en el porcentaje
        updateProgressBarColor(progressBar, percentage);
    });
}

/**
 * Anima una barra de progreso
 */
function animateProgressBar(progressBar, targetPercentage) {
    progressBar.style.width = `${targetPercentage}%`;
    
    // Animación con contador visual
    let currentWidth = 0;
    const increment = targetPercentage / 50;
    
    const animate = () => {
        currentWidth += increment;
        if (currentWidth >= targetPercentage) {
            progressBar.style.width = `${targetPercentage}%`;
            return;
        }
        
        progressBar.style.width = `${currentWidth}%`;
        requestAnimationFrame(animate);
    };
    
    animate();
}

/**
 * Actualiza el color de la barra de progreso
 */
function updateProgressBarColor(progressBar, percentage) {
    if (percentage >= 90) {
        progressBar.style.background = 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)';
    } else if (percentage >= 70) {
        progressBar.style.background = 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)';
    } else {
        progressBar.style.background = 'linear-gradient(135deg, #10B981 0%, #059669 100%)';
    }
}

/**
 * Inicializa contadores animados para las estadísticas de uso
 */
function initializeUsageCounters() {
    const counters = document.querySelectorAll('.usage-numbers .current');
    
    counters.forEach((counter, index) => {
        const target = parseFloat(counter.textContent) || 0;
        
        setTimeout(() => {
            animateCounter(counter, target);
        }, index * 200);
    });
}

/**
 * Anima un contador numérico
 */
function animateCounter(element, target) {
    let current = 0;
    const increment = target / 30;
    const duration = 800;
    const stepDuration = duration / 30;
    
    const animate = () => {
        current += increment;
        if (current >= target) {
            element.textContent = target % 1 === 0 ? target : target.toFixed(1);
            return;
        }
        
        element.textContent = current % 1 === 0 ? Math.floor(current) : current.toFixed(1);
        setTimeout(animate, stepDuration);
    };
    
    animate();
}

/**
 * Inicializa las opciones de planes
 */
function initializePlanOptions() {
    const planOptions = document.querySelectorAll('.plan-item');
    
    planOptions.forEach((option, index) => {
        // Animación de entrada escalonada
        option.style.opacity = '0';
        option.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            option.style.transition = 'all 0.4s ease';
            option.style.opacity = '1';
            option.style.transform = 'translateY(0)';
        }, index * 100);
        
        // Manejar selección de plan
        const selectButton = option.querySelector('.plan-select-button');
        if (selectButton) {
            selectButton.addEventListener('click', function(e) {
                handlePlanSelection(e, option);
            });
        }
    });
}

/**
 * Maneja la selección de un plan
 */
function handlePlanSelection(event, planOption) {
    const planName = planOption.querySelector('h4').textContent;
    
    // Efecto visual en el botón
    const button = event.target;
    const originalContent = button.innerHTML;
    
    button.style.transform = 'scale(0.95)';
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Seleccionando...';
    
    setTimeout(() => {
        button.style.transform = 'scale(1)';
        button.innerHTML = originalContent;
    }, 1000);
    
    console.log(`Plan seleccionado: ${planName}`);
}

/**
 * Inicializa el contador regresivo del trial
 */
function initializeTrialCountdown() {
    const countdownElement = document.querySelector('.countdown-number');
    if (!countdownElement) return;
    
    const daysRemaining = parseInt(countdownElement.textContent) || 0;
    
    // Animar el número
    let currentDay = 0;
    const increment = daysRemaining / 20;
    const stepDuration = 50;
    
    const animate = () => {
        currentDay += increment;
        if (currentDay >= daysRemaining) {
            countdownElement.textContent = daysRemaining;
            // Agregar pulsación si quedan pocos días
            if (daysRemaining <= 7) {
                countdownElement.style.animation = 'pulse 2s infinite';
            }
            return;
        }
        
        countdownElement.textContent = Math.floor(currentDay);
        setTimeout(animate, stepDuration);
    };
    
    animate();
}

/**
 * Inicializa animaciones básicas
 */
function initializeAnimations() {
    // Observador para animaciones al hacer scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Observar elementos animables
    const animatableElements = document.querySelectorAll('.usage-card, .feature-item, .payment-item');
    animatableElements.forEach(element => {
        observer.observe(element);
    });
    
    // Animación del hero card
    const heroCard = document.querySelector('.plan-hero-card');
    if (heroCard) {
        heroCard.style.opacity = '0';
        heroCard.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            heroCard.style.transition = 'all 0.6s ease';
            heroCard.style.opacity = '1';
            heroCard.style.transform = 'translateY(0)';
        }, 200);
    }
}

/**
 * Utilidades para el manejo de datos de uso
 */
const UsageUtils = {
    /**
     * Formatea bytes a una unidad legible
     */
    formatBytes: function(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    /**
     * Calcula el porcentaje de uso
     */
    calculatePercentage: function(current, limit) {
        if (limit === 0) return 0;
        return Math.min((current / limit) * 100, 100);
    },

    /**
     * Determina el estado del uso basado en el porcentaje
     */
    getUsageStatus: function(percentage) {
        if (percentage >= 90) return 'danger';
        if (percentage >= 70) return 'warning';
        return 'good';
    }
};

/**
 * API simplificada para comunicación con el backend
 */
const PlansAPI = {
    /**
     * Obtiene el token CSRF
     */
    getCsrfToken: function() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    },

    /**
     * Obtiene los datos actualizados de uso
     */
    getUsageData: async function() {
        try {
            const response = await fetch('/api/plans/usage/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            
            if (!response.ok) {
                throw new Error('Error al obtener datos de uso');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }
};

/**
 * Funciones de utilidad simplificadas
 */
const PlanUtils = {
    /**
     * Muestra notificación simple
     */
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `simple-notification notification-${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 12px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        
        if (type === 'success') notification.style.background = '#10B981';
        else if (type === 'error') notification.style.background = '#EF4444';
        else if (type === 'warning') notification.style.background = '#F59E0B';
        else notification.style.background = '#4F46E5';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
};

// Agregar estilos CSS para las animaciones básicas
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }
    
    .simple-notification {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
`;
document.head.appendChild(style);

// ========================================
// TRIAL NOTIFICATION COMPONENT FUNCTIONALITY - MEJORADO
// ========================================

// Configuration
const REMIND_LATER_DURATION = 24 * 60 * 60 * 1000; // 24 horas en milisegundos
const STORAGE_KEY = 'trial_notification_hidden_until';

// Agregar inicialización del banner a la función principal
const originalInitialize = initializeSubscriptionDashboard;
initializeSubscriptionDashboard = function() {
    originalInitialize();
    initializeTrialNotification();
};

/**
 * Initialize the trial notification component
 */
function initializeTrialNotification() {
    const notification = document.getElementById('trial-notification') || 
                        document.getElementById('renewal-notification');
    
    if (!notification) return;
    
    // Check if notification should be hidden
    if (shouldHideNotification()) {
        hideNotification(notification, false);
        return;
    }
    
    // Add event listeners
    setupEventListeners(notification);
    
    // Show notification with animation
    showNotification(notification);
    
    // Animate counter if it's a trial notification
    if (notification.id === 'trial-notification') {
        animateCounter();
    }
}

/**
 * Check if notification should be hidden based on "remind later" setting
 */
function shouldHideNotification() {
    const hiddenUntil = localStorage.getItem(STORAGE_KEY);
    if (!hiddenUntil) return false;
    
    const hiddenUntilTime = parseInt(hiddenUntil, 10);
    const currentTime = Date.now();
    
    if (currentTime < hiddenUntilTime) {
        return true;
    } else {
        // Clear expired storage
        localStorage.removeItem(STORAGE_KEY);
        return false;
    }
}

/**
 * Setup event listeners for the notification
 */
function setupEventListeners(notification) {
    // Remind later button
    const remindLaterBtn = notification.querySelector('.remind-later-btn');
    if (remindLaterBtn) {
        remindLaterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            remindLater();
        });
    }
    
    // Upgrade button tracking
    const upgradeBtn = notification.querySelector('.upgrade-btn');
    if (upgradeBtn) {
        upgradeBtn.addEventListener('click', function() {
            // Optional: Track upgrade button clicks
            console.log('Upgrade button clicked');
            // You can add analytics tracking here
        });
    }
}

/**
 * Handle "remind later" functionality
 */
function remindLater() {
    const notification = document.getElementById('trial-notification') || 
                        document.getElementById('renewal-notification');
    
    if (!notification) return;
    
    // Store the time when notification should be shown again
    const hideUntil = Date.now() + REMIND_LATER_DURATION;
    localStorage.setItem(STORAGE_KEY, hideUntil.toString());
    
    // Hide notification with animation
    hideNotification(notification, true);
    
    // Show confirmation message
    showRemindLaterConfirmation();
}

/**
 * Hide notification with smooth animation
 */
function hideNotification(notification, animate = true) {
    if (!notification) return;
    
    if (animate) {
        notification.style.transition = 'all 0.4s ease-out';
        notification.style.transform = 'translateY(-20px)';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            notification.style.display = 'none';
        }, 400);
    } else {
        notification.style.display = 'none';
    }
}

/**
 * Show notification with smooth animation
 */
function showNotification(notification) {
    if (!notification) return;
    
    notification.style.display = 'block';
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    
    // Force reflow
    notification.offsetHeight;
    
    notification.style.transition = 'all 0.6s ease-out';
    notification.style.opacity = '1';
    notification.style.transform = 'translateY(0)';
}

/**
 * Show confirmation message for "remind later"
 */
function showRemindLaterConfirmation() {
    // Create temporary toast notification
    const toast = document.createElement('div');
    toast.className = 'alert alert-info alert-dismissible fade show position-fixed';
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
        animation: fadeInSlideDown 0.3s ease-out;
    `;
    
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-check-circle me-2 text-success"></i>
            <div>
                <strong>¡Perfecto!</strong><br>
                <small>Te recordaremos mañana sobre tu prueba gratuita.</small>
            </div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'fadeOutSlideUp 0.3s ease-out';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }, 4000);
}

/**
 * Animate counter from 0 to actual days remaining
 */
function animateCounter() {
    const badgeElement = document.querySelector('.trial-countdown-container .badge');
    if (!badgeElement) return;
    
    const finalNumber = parseInt(badgeElement.textContent);
    if (isNaN(finalNumber)) return;
    
    let currentNumber = 0;
    const increment = finalNumber / 30; // 30 steps for smooth animation
    const duration = 1000; // 1 second total
    const stepTime = duration / 30;
    
    // Set initial value
    badgeElement.textContent = '0';
    
    const timer = setInterval(() => {
        currentNumber += increment;
        
        if (currentNumber >= finalNumber) {
            badgeElement.textContent = finalNumber;
            badgeElement.classList.add('counter-animate');
            clearInterval(timer);
            
            // Remove animation class after it completes
            setTimeout(() => {
                badgeElement.classList.remove('counter-animate');
            }, 100);
        } else {
            badgeElement.textContent = Math.floor(currentNumber);
            
            // Add small pop animation every 5 steps
            if (Math.floor(currentNumber) % 5 === 0) {
                badgeElement.classList.add('counter-animate');
                setTimeout(() => {
                    badgeElement.classList.remove('counter-animate');
                }, 100);
            }
        }
    }, stepTime);
}

/**
 * Utility function to check trial urgency and update UI accordingly
 */
function updateTrialUrgency(daysRemaining) {
    const notification = document.getElementById('trial-notification');
    if (!notification) return;
    
    const badge = notification.querySelector('.badge');
    const icon = notification.querySelector('.trial-icon');
    
    // Remove existing urgency classes
    notification.classList.remove('bg-primary', 'bg-warning', 'bg-danger');
    badge?.classList.remove('bg-light', 'text-primary', 'text-warning', 'text-danger', 'countdown-pulse');
    icon?.classList.remove('pulse-animation');
    
    // Apply appropriate classes based on days remaining
    if (daysRemaining >= 8) {
        notification.classList.add('bg-primary', 'bg-gradient');
        badge?.classList.add('bg-light', 'text-primary');
    } else if (daysRemaining >= 3) {
        notification.classList.add('bg-warning', 'bg-gradient');
        badge?.classList.add('bg-light', 'text-warning');
    } else {
        notification.classList.add('bg-danger', 'bg-gradient');
        badge?.classList.add('bg-light', 'text-danger', 'countdown-pulse');
        icon?.classList.add('pulse-animation');
    }
}

/**
 * Reset "remind later" setting (useful for testing or admin purposes)
 */
function resetRemindLater() {
    localStorage.removeItem(STORAGE_KEY);
    location.reload();
}

// Add CSS for toast animations
const toastStyle = document.createElement('style');
toastStyle.textContent = `
    @keyframes fadeInSlideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeOutSlideUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
`;
document.head.appendChild(toastStyle);

// Create TrialNotification object for external use
window.TrialNotification = {
    remindLater,
    resetRemindLater,
    updateTrialUrgency,
    hideNotification,
    showNotification,
    animateCounter
};

// Exportar funciones para uso global si es necesario
window.PlansAPI = PlansAPI;
window.PlanUtils = PlanUtils;
window.UsageUtils = UsageUtils;
