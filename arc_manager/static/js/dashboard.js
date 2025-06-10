// Dashboard JavaScript - Extiende BaseAnimation
class DashboardManager extends BaseAnimation {
    constructor() {
        super();
        this.initializeDashboard();
    }

    initializeDashboard() {
        // Inicializar animaciones específicas del dashboard
        this.initializeDashboardAnimations();
        this.initializeProgressBars();
        this.initializeTooltips();
    }

    initializeDashboardAnimations() {
        // Animar las tarjetas del dashboard
        this.animateElements('.dashboard-card', {
            delay: 0,
            stagger: 100,
            distance: 20,
            duration: 0.3
        });

        // Animar elementos de actividad
        this.animateElements('.dashboard-activity-item', {
            delay: 300,
            stagger: 50,
            distance: 20,
            duration: 0.3
        });
    }

    initializeProgressBars() {
        const progressBars = document.querySelectorAll('.dashboard-progress-bar');
        progressBars.forEach(bar => {
            const targetWidth = bar.getAttribute('data-progress') + '%';
            bar.style.width = '0';
            
            setTimeout(() => {
                bar.style.width = targetWidth;
            }, 300);
        });
    }

    initializeTooltips() {
        // Inicializar tooltips de Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover'
            });
        });
    }

    updateCardValue(cardId, newValue, animate = true) {
        const card = document.querySelector(`#${cardId} .dashboard-card-value`);
        if (!card) return;

        if (animate) {
            const oldValue = parseInt(card.textContent);
            const diff = newValue - oldValue;
            const duration = 1000;
            const steps = 20;
            const stepValue = diff / steps;
            let currentStep = 0;

            const interval = setInterval(() => {
                currentStep++;
                const currentValue = Math.round(oldValue + (stepValue * currentStep));
                card.textContent = currentValue;

                if (currentStep >= steps) {
                    clearInterval(interval);
                    card.textContent = newValue;
                }
            }, duration / steps);
        } else {
            card.textContent = newValue;
        }
    }

    updateProgressBar(barId, newProgress) {
        const bar = document.querySelector(`#${barId} .dashboard-progress-bar`);
        if (!bar) return;

        bar.style.width = `${newProgress}%`;
        bar.setAttribute('data-progress', newProgress);
    }

    animateStatsCards() {
        // Animar aparición de tarjetas estadísticas
        const cards = document.querySelectorAll('.dashboard-stat-card');
        cards.forEach((card, idx) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            setTimeout(() => {
                card.style.transition = 'all 0.5s cubic-bezier(.4,2,.3,1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + idx * 120);
        });
    }

    animateProgressBars() {
        // Animar barras de progreso
        const bars = document.querySelectorAll('.dashboard-progress-bar .progress-bar');
        bars.forEach(bar => {
            const target = parseInt(bar.getAttribute('aria-valuenow')) || 0;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = 'width 1s cubic-bezier(.4,2,.3,1)';
                bar.style.width = target + '%';
            }, 400);
        });
    }
}

// Inicializar el dashboard cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardManager = new DashboardManager();
    initMetricCardEffects();
    initTooltipEnhancements();
    initTrendAnimations();
    initCounterAnimations();
});

// ===== MEJORAS INTERACTIVAS PARA EL DASHBOARD =====

// Efectos mejorados para las cards de métricas
function initMetricCardEffects() {
    const metricCards = document.querySelectorAll('.metric-card, .dashboard-stat-card');
    
    metricCards.forEach(card => {
        // Efecto parallax suave al hover
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px) scale(1.02)';
            
            // Efecto en el icono
            const icon = this.querySelector('.dashboard-card-icon, .stat-icon-lg');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            
            // Restablecer icono
            const icon = this.querySelector('.dashboard-card-icon, .stat-icon-lg');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
        
        // Efecto de click/tap
        card.addEventListener('click', function() {
            this.style.transform = 'translateY(-2px) scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'translateY(-4px) scale(1.02)';
            }, 100);
        });
    });
}

// Tooltips mejorados con animaciones
function initTooltipEnhancements() {
    const elementsWithTooltip = document.querySelectorAll('[data-tooltip]');
    
    elementsWithTooltip.forEach(element => {
        element.addEventListener('mouseenter', function() {
            // Agregar clase para animación personalizada
            this.classList.add('tooltip-active');
        });
        
        element.addEventListener('mouseleave', function() {
            this.classList.remove('tooltip-active');
        });
    });
}

// Animaciones para indicadores de tendencia
function initTrendAnimations() {
    const trendIndicators = document.querySelectorAll('.trend-indicator');
    
    // Observador de intersección para animar cuando entran en vista
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, 200);
                
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    trendIndicators.forEach(indicator => {
        observer.observe(indicator);
    });
}

// Animaciones de contador para los números
function initCounterAnimations() {
    const valueElements = document.querySelectorAll('.kpi-value, .stat-value, .stat-number-simple');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    valueElements.forEach(element => {
        observer.observe(element);
    });
}

// Función para animar contadores
function animateCounter(element) {
    const text = element.textContent;
    const number = parseFloat(text.replace(/[^\d.]/g, ''));
    
    if (isNaN(number)) return;
    
    const suffix = text.replace(number.toString(), '');
    const increment = number / 50; // 50 frames de animación
    let current = 0;
    
    element.textContent = '0' + suffix;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= number) {
            current = number;
            clearInterval(timer);
        }
        
        let displayValue;
        if (number >= 1000000) {
            displayValue = (current / 1000000).toFixed(1) + 'M';
        } else if (number >= 1000) {
            displayValue = (current / 1000).toFixed(1) + 'K';
        } else if (number % 1 !== 0) {
            displayValue = current.toFixed(1);
        } else {
            displayValue = Math.floor(current).toString();
        }
        
        element.textContent = displayValue + suffix.replace(/[MK\d.]/g, '');
    }, 30);
}

// Efectos de partículas para las cards (opcional)
function createParticleEffect(element) {
    const rect = element.getBoundingClientRect();
    const particle = document.createElement('div');
    
    particle.style.cssText = `
        position: fixed;
        width: 4px;
        height: 4px;
        background: #3b82f6;
        border-radius: 50%;
        pointer-events: none;
        z-index: 1000;
        left: ${rect.left + rect.width / 2}px;
        top: ${rect.top + rect.height / 2}px;
        opacity: 1;
        transition: all 0.6s ease-out;
    `;
    
    document.body.appendChild(particle);
    
    // Animar partícula
    requestAnimationFrame(() => {
        particle.style.transform = `translate(${(Math.random() - 0.5) * 100}px, ${(Math.random() - 0.5) * 100}px)`;
        particle.style.opacity = '0';
    });
    
    // Limpiar después de la animación
    setTimeout(() => {
        document.body.removeChild(particle);
    }, 600);
}

// Función para actualizar métricas dinámicamente (simulada)
function updateMetrics() {
    const metrics = [
        { selector: '.kpi1 .kpi-value', value: Math.floor(Math.random() * 1000) + 3000 },
        { selector: '.kpi2 .kpi-value', value: (Math.random() * 2 + 4).toFixed(1) + 'M' },
        { selector: '.kpi3 .kpi-value', value: Math.floor(Math.random() * 20) + 70 + '%' }
    ];
    
    metrics.forEach(metric => {
        const element = document.querySelector(metric.selector);
        if (element) {
            // Efecto de fade out/in para el cambio
            element.style.transition = 'opacity 0.3s ease';
            element.style.opacity = '0';
            
            setTimeout(() => {
                element.textContent = metric.value;
                element.style.opacity = '1';
                
                // Efecto de highlight
                element.style.background = 'rgba(59, 130, 246, 0.1)';
                element.style.borderRadius = '4px';
                element.style.padding = '2px 4px';
                
                setTimeout(() => {
                    element.style.background = 'transparent';
                    element.style.padding = '0';
                }, 1000);
            }, 300);
        }
    });
}

// Efectos de pulse para indicadores importantes
function pulseIndicators() {
    const indicators = document.querySelectorAll('.trend-indicator.positive');
    
    indicators.forEach(indicator => {
        indicator.style.animation = 'pulse 2s infinite';
    });
}

// Estilos CSS dinámicos para las animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        }
        50% { 
            transform: scale(1.05);
            box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
        }
    }
    
    .tooltip-active {
        position: relative;
        z-index: 1001;
    }
    
    .metric-card {
        cursor: pointer;
        position: relative;
        overflow: visible;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
        pointer-events: none;
    }
    
    .metric-card:hover::after {
        transform: translateX(100%);
    }
`;
document.head.appendChild(style);

// Inicializar efectos adicionales cuando todo esté cargado
window.addEventListener('load', function() {
    // Pulsar indicadores después de 2 segundos
    setTimeout(pulseIndicators, 2000);
    
    // Actualizar métricas cada 30 segundos (para demo)
    // setInterval(updateMetrics, 30000);
});

// ===== COMPATIBILIDAD Y ACCESIBILIDAD =====

// Reducir animaciones si el usuario prefiere menos movimiento
if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    // Deshabilitar animaciones complejas
    const style = document.createElement('style');
    style.textContent = `
        .metric-card, .dashboard-stat-card, .trend-indicator {
            transition: none !important;
            animation: none !important;
        }
    `;
    document.head.appendChild(style);
}

// Soporte para touch en dispositivos móviles
if ('ontouchstart' in window) {
    document.addEventListener('touchstart', function(e) {
        if (e.target.closest('.metric-card')) {
            createParticleEffect(e.target.closest('.metric-card'));
        }
    });
} 