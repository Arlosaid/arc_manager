/**
 * Dashboard Premium - Lógica de Interacción Avanzada
 * Versión moderna con animaciones fluidas y microinteracciones.
 */

class Dashboard {
    constructor() {
        this.init();
        this.observers = new Map();
        this.animationQueue = [];
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    init() {
        this.setupIntersectionObserver();
        this.initializeGreeting();
        this.initializeCounters();
        this.initializeInteractions();
        this.initializeParallax();
        this.initializeScrollAnimations();
        this.initializeHoverEffects();
        this.initializeDashboardData();
    }

    // ===== OBSERVER PARA ANIMACIONES AL SCROLL =====
    setupIntersectionObserver() {
        if (this.isReducedMotion) return;

        const options = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.triggerAnimation(entry.target);
                }
            });
        }, options);

        // Observar elementos que necesiten animación al aparecer en viewport
        document.querySelectorAll('.metric-card, .project-card-compact, .task-card-compact, .document-card-compact, .activity-item').forEach(el => {
            this.observer.observe(el);
        });
    }

    triggerAnimation(element) {
        element.classList.add('animate-in');
        if (element.classList.contains('metric-card')) {
            this.animateMetricCard(element);
        }
    }

    // ===== SALUDO DINÁMICO CON EFECTO TYPING =====
    initializeGreeting() {
        const greetingElement = document.querySelector('.time-greeting');
        if (!greetingElement) return;
        
        const hour = new Date().getHours();
        let greeting = 'Buenos días';
        
        if (hour >= 12 && hour < 18) {
            greeting = 'Buenas tardes';
        } else if (hour >= 18) {
            greeting = 'Buenas noches';
        }

        // Efecto de typing suave
        this.typeText(greetingElement, greeting, 100);

        // Animar el nombre del usuario con efecto de reveal
        this.animateUserName();
    }

    typeText(element, text, speed = 50) {
        if (this.isReducedMotion) {
            element.textContent = text;
            return;
        }

        element.textContent = '';
        element.style.opacity = '1';
        
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
                element.classList.add('typing-complete');
            }
        }, speed);
    }

    animateUserName() {
        const userNameElement = document.querySelector('.user-name');
        if (!userNameElement || this.isReducedMotion) return;

        // Agregar efecto de reveal con retraso
        setTimeout(() => {
            userNameElement.classList.add('name-revealed');
        }, 800);
    }

    // ===== CONTADORES ANIMADOS MEJORADOS =====
    initializeCounters() {
        const counterElements = document.querySelectorAll('.metric-value[data-target]');
        
        counterElements.forEach((element, index) => {
            // Retrasar cada contador para efecto escalonado
            setTimeout(() => {
                this.animateCounter(element);
            }, index * 200);
        });
    }

    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-target')) || 0;
        const duration = this.isReducedMotion ? 100 : 2500;
        const stepTime = 16;
        const increment = target / steps;
        let current = 0;

        // Función de easing para suavizar la animación
        const easeOutQuart = (t) => 1 - (--t) * t * t * t;

        const startTime = performance.now();
        
        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Aplicar easing
            const easedProgress = easeOutQuart(progress);
            current = target * easedProgress;
            
            element.textContent = this.formatNumber(Math.floor(current));
            
            // Efecto de pulso al completar
            if (progress >= 1) {
                element.classList.add('counter-complete');
                this.addPulseEffect(element);
            } else {
                requestAnimationFrame(updateCounter);
            }
        };

        requestAnimationFrame(updateCounter);
    }

    addPulseEffect(element) {
        if (this.isReducedMotion) return;
        
        element.style.transform = 'scale(1.1)';
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 300);
    }

    formatNumber(num) {
        return num.toLocaleString('es-ES');
    }

    // ===== INTERACCIONES AVANZADAS =====
    initializeInteractions() {
        this.setupRefreshButton();
        this.setupCardInteractions();
        this.setupProjectCards();
        this.setupTaskCards();
        this.setupDocumentCards();
        this.setupActivityItems();
        // Sidebar del dashboard eliminado
    }

    setupRefreshButton() {
        // Botón de actualizar actividades removido
        return;
    }

    createRippleEffect(element, event) {
        if (this.isReducedMotion) return;

        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            z-index: 10;
        `;
        
        element.style.position = 'relative';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    refreshActivities() {
        const activityItems = document.querySelectorAll('.activity-item');
        
        // Animar salida
        activityItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.transform = 'translateX(-100%)';
                item.style.opacity = '0';
            }, index * 50);
        });

        // Simular nueva data y animar entrada
        setTimeout(() => {
            activityItems.forEach((item, index) => {
                setTimeout(() => {
                    item.style.transform = 'translateX(0)';
                    item.style.opacity = '1';
                    item.style.transition = 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
                }, index * 100);
            });
        }, 500);
    }

    setupCardInteractions() {
        const metricCards = document.querySelectorAll('.metric-card');
        
        metricCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.enhanceMetricCard(card);
            });
            
            card.addEventListener('mouseleave', () => {
                this.resetMetricCard(card);
            });
        });
    }

    enhanceMetricCard(card) {
        if (this.isReducedMotion) return;
        
        const icon = card.querySelector('.metric-icon i');
        const value = card.querySelector('.metric-value');
        
        if (icon) {
            icon.style.animation = 'iconBounce 0.6s ease-in-out';
        }
        
        if (value) {
            value.style.textShadow = '0 0 10px rgba(37, 99, 235, 0.3)';
        }
    }

    resetMetricCard(card) {
        const icon = card.querySelector('.metric-icon i');
        const value = card.querySelector('.metric-value');
        
        if (icon) {
            icon.style.animation = '';
        }
        
        if (value) {
            value.style.textShadow = '';
        }
    }

    setupProjectCards() {
        const projectCards = document.querySelectorAll('.project-card-compact');
        
        projectCards.forEach((card, index) => {
            card.addEventListener('mouseenter', () => {
                this.animateProjectCard(card, 'enter');
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateProjectCard(card, 'leave');
            });
        });
    }

    animateProjectCard(card, action) {
        if (this.isReducedMotion) return;
        
        const image = card.querySelector('.project-image-compact');
        const name = card.querySelector('.project-name-compact');
        
        if (action === 'enter') {
            if (image) {
                image.style.filter = 'brightness(1.1) saturate(1.2)';
            }
            if (name) {
                name.style.letterSpacing = '0.5px';
            }
        } else {
            if (image) {
                image.style.filter = '';
            }
            if (name) {
                name.style.letterSpacing = '';
            }
        }
    }

    setupTaskCards() {
        const taskCards = document.querySelectorAll('.task-card-compact');
        
        taskCards.forEach((card, index) => {
            card.addEventListener('mouseenter', () => {
                this.animateTaskCard(card, 'enter');
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateTaskCard(card, 'leave');
            });
        });
    }

    animateTaskCard(card, action) {
        if (this.isReducedMotion) return;
        
        const image = card.querySelector('.task-image-compact');
        const name = card.querySelector('.task-name-compact');
        
        if (action === 'enter') {
            if (image) {
                image.style.filter = 'brightness(1.1) saturate(1.2)';
            }
            if (name) {
                name.style.letterSpacing = '0.5px';
            }
        } else {
            if (image) {
                image.style.filter = '';
            }
            if (name) {
                name.style.letterSpacing = '';
            }
        }
    }

    setupDocumentCards() {
        const documentCards = document.querySelectorAll('.document-card-compact');
        
        documentCards.forEach((card, index) => {
            card.addEventListener('mouseenter', () => {
                this.animateDocumentCard(card, 'enter');
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateDocumentCard(card, 'leave');
            });
        });
    }

    animateDocumentCard(card, action) {
        if (this.isReducedMotion) return;
        
        const image = card.querySelector('.document-image-compact');
        const name = card.querySelector('.document-name-compact');
        
        if (action === 'enter') {
            if (image) {
                image.style.filter = 'brightness(1.1) saturate(1.2)';
            }
            if (name) {
                name.style.letterSpacing = '0.5px';
            }
        } else {
            if (image) {
                image.style.filter = '';
            }
            if (name) {
                name.style.letterSpacing = '';
            }
        }
    }

    setupActivityItems() {
        const activityItems = document.querySelectorAll('.activity-item');
        
        activityItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                this.highlightActivity(item);
            });
        });
    }

    highlightActivity(item) {
        if (this.isReducedMotion) return;
        
        // Efecto de highlight temporal
        item.style.background = 'rgba(37, 99, 235, 0.15)';
        item.style.transform = 'scale(1.02)';
        
        setTimeout(() => {
            item.style.background = '';
            item.style.transform = '';
        }, 1000);
    }

    // Funciones del sidebar del dashboard eliminadas

    // ===== EFECTOS DE PARALLAX SUTIL =====
    initializeParallax() {
        if (this.isReducedMotion) return;
        
        const welcomeSection = document.querySelector('.welcome-section');
        if (!welcomeSection) return;

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            welcomeSection.style.transform = `translateY(${rate}px)`;
        });
    }

    // ===== ANIMACIONES AL SCROLL =====
    initializeScrollAnimations() {
        // REMOVIDO: Esta función causaba problemas de visibilidad en el sidebar
        // Los elementos ahora son visibles por defecto sin necesidad de animaciones de scroll
        return;
    }

    // ===== EFECTOS DE HOVER DINÁMICOS =====
    initializeHoverEffects() {
        this.setupMagneticEffect();
        this.setupGlowEffect();
    }

    setupMagneticEffect() {
        if (this.isReducedMotion) return;
        
        const buttons = document.querySelectorAll('.quick-action-btn, .refresh-btn');
        
        buttons.forEach(button => {
            button.addEventListener('mousemove', (e) => {
                const rect = button.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                button.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = '';
            });
        });
    }

    setupGlowEffect() {
        if (this.isReducedMotion) return;
        
        const cards = document.querySelectorAll('.metric-card');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                card.style.setProperty('--glow-x', `${x}px`);
                card.style.setProperty('--glow-y', `${y}px`);
            });
        });
    }

    // ===== GESTIÓN DE DATOS DEL DASHBOARD =====
    initializeDashboardData(metrics = {}) {
        // Usar datos del servidor si están disponibles, sino usar datos por defecto
        const serverMetrics = window.serverData || this.getSimulatedData();
        
        window.dashboardData = {
            chartData: {
                users_monthly: [
                    { month: 'Ene', value: serverMetrics.newUsersThisMonth || 45 },
                    { month: 'Feb', value: serverMetrics.totalUsers || 52 },
                    { month: 'Mar', value: 68 },
                    { month: 'Abr', value: 84 },
                    { month: 'May', value: 102 },
                    { month: 'Jun', value: 125 }
                ],
                orgs_monthly: [
                    { month: 'Ene', value: 12 },
                    { month: 'Feb', value: 15 },
                    { month: 'Mar', value: 18 },
                    { month: 'Abr', value: 22 },
                    { month: 'May', value: 28 },
                    { month: 'Jun', value: 35 }
                ],
                revenue_monthly: [
                    { month: 'Ene', value: 8500 },
                    { month: 'Feb', value: 9200 },
                    { month: 'Mar', value: 11200 },
                    { month: 'Abr', value: 13800 },
                    { month: 'May', value: 15200 },
                    { month: 'Jun', value: 18400 }
                ]
            },
            metrics: {
                totalUsers: serverMetrics.totalUsers || 0,
                totalOrganizations: serverMetrics.totalOrganizations || 0,
                totalSubscriptions: serverMetrics.totalSubscriptions || 0,
                userGrowth: metrics.userGrowth || 0,
                orgGrowth: metrics.orgGrowth || 0,
                newUsersThisMonth: metrics.newUsersThisMonth || 0,
                newOrgsThisMonth: metrics.newOrgsThisMonth || 0,
                subscriptionRate: metrics.subscriptionRate || 0,
                pendingUpgrades: metrics.pendingUpgrades || 0
            },
            timestamps: {
                lastUpdate: new Date().toISOString(),
                nextUpdate: new Date(Date.now() + 30000).toISOString() // 30 segundos
            }
        };
        
        console.log('Dashboard data initialized:', window.dashboardData);
    }

    // Función para actualizar métricas en tiempo real
    updateDashboardMetrics(newMetrics) {
        if (!window.dashboardData) {
            this.initializeDashboardData(newMetrics);
            return;
        }
        
        // Actualizar métricas
        Object.assign(window.dashboardData.metrics, newMetrics);
        
        // Actualizar timestamp
        window.dashboardData.timestamps.lastUpdate = new Date().toISOString();
        
        // Disparar evento personalizado para notificar cambios
        window.dispatchEvent(new CustomEvent('dashboardDataUpdated', {
            detail: { metrics: newMetrics }
        }));
        
        // Actualizar contadores visualmente
        this.updateCountersWithNewData(newMetrics);
    }

    updateCountersWithNewData(metrics) {
        // Actualizar los data-target de los contadores
        const counterMappings = {
            'totalUsers': metrics.totalUsers,
            'totalOrganizations': metrics.totalOrganizations,
            'totalSubscriptions': metrics.totalSubscriptions
        };

        Object.entries(counterMappings).forEach(([key, value]) => {
            if (value !== undefined) {
                const element = document.querySelector(`[data-target="${window.dashboardData.metrics[key]}"]`);
                if (element) {
                    element.setAttribute('data-target', value);
                    this.animateCounter(element);
                }
            }
        });
    }

    // Función para obtener datos simulados para demo
    getSimulatedData() {
        return {
            totalUsers: 1247,
            totalOrganizations: 89,
            totalSubscriptions: 156,
            userGrowth: 15.2,
            orgGrowth: 8.7,
            newUsersThisMonth: 45,
            newOrgsThisMonth: 12,
            subscriptionRate: 12.5,
            pendingUpgrades: 7
        };
    }

    // ===== FUNCIONES DE UTILIDAD =====
    animateMetricCard(card) {
        if (this.isReducedMotion) return;
        
        const value = card.querySelector('.metric-value');
        const icon = card.querySelector('.metric-icon');
        
        if (value && !value.classList.contains('animated')) {
            value.classList.add('animated');
            this.animateCounter(value);
        }
        
        if (icon) {
            icon.style.animation = 'iconBounce 0.6s ease-in-out';
        }
    }

    // ===== LIMPIEZA =====
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        this.observers.forEach(observer => {
            observer.disconnect();
        });
        
        this.observers.clear();
        this.animationQueue = [];
    }
}

// ===== CSS DINÁMICO PARA ANIMACIONES ADICIONALES =====
const additionalStyles = `
@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.metric-card {
    --glow-x: 50%;
    --glow-y: 50%;
}

.metric-card:hover::after {
    background: radial-gradient(circle at var(--glow-x) var(--glow-y), rgba(37, 99, 235, 0.1) 0%, transparent 50%);
}

/* REMOVIDO: animación scroll-revealed que causaba problemas de visibilidad */

.typing-complete::after {
    content: '';
    display: inline-block;
    width: 2px;
    height: 1em;
    background: currentColor;
    margin-left: 2px;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

.name-revealed {
    animation: nameReveal 1s ease-out both;
}

@keyframes nameReveal {
    from {
        background-position: -200% 50%;
        filter: blur(2px);
    }
    to {
        background-position: 200% 50%;
        filter: blur(0);
    }
}

.counter-complete {
    animation: counterPulse 0.6s ease-out both;
}

@keyframes counterPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); filter: brightness(1.1); }
    100% { transform: scale(1); filter: brightness(1); }
}

@media (prefers-reduced-motion: reduce) {
    .typing-complete::after,
    .name-revealed,
    .counter-complete {
        animation: none !important;
    }
}
`;

// Inyectar estilos adicionales
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Inicialización del dashboard mejorado
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
    
    // Configurar datos del servidor si están disponibles
    if (window.serverData) {
        console.log('Dashboard inicializado con datos del servidor:', window.serverData);
    }
    
    // Exponer funciones globalmente para compatibilidad
    window.updateDashboardMetrics = (metrics) => {
        if (window.dashboard) {
            window.dashboard.updateDashboardMetrics(metrics);
        }
    };
});

// Limpieza al cerrar la página
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});

// Dashboard optimizado para rendimiento
(function() {
    'use strict';
    
    // Configuración optimizada
    const config = {
        counterSpeed: 100, // Reducido para mejor rendimiento
        animationDelay: 300, // Delay para animaciones
        reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
    };
    
    // Cache de elementos DOM
    const elements = {
        timeGreeting: document.getElementById('time-greeting'),
        counters: document.querySelectorAll('.metric-value[data-target]'),
        refreshBtn: document.getElementById('refresh-activities')
    };
    
    // Saludo dinámico optimizado
    function updateGreeting() {
        if (!elements.timeGreeting) return;
        const hour = new Date().getHours();
        let greeting;
        if (hour < 12) greeting = 'Buenos días';
        else if (hour < 18) greeting = 'Buenas tardes';
        else greeting = 'Buenas noches';
        if (elements.timeGreeting.textContent !== greeting) {
            elements.timeGreeting.textContent = greeting;
        }
    }
    
    // Animación de contadores optimizada con requestAnimationFrame
    function animateCounters() {
        if (!elements.counters || config.reducedMotion) return;
        
        elements.counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'), 10) || 0;
            if (target === 0) {
                counter.textContent = 0;
                return;
            }
            const increment = Math.max(1, Math.ceil(target / config.counterSpeed));
            let current = 0;
            
            function updateCounter() {
                current += increment;
                if (current < target) {
                    counter.textContent = Math.ceil(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            }
            updateCounter();
        });
    }
    
    // Botón de refrescar optimizado
    function initRefreshButton() {
        if (!elements.refreshBtn) return;
        
        elements.refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (this.classList.contains('spinning')) return;
            
            const icon = this.querySelector('i');
            this.classList.add('spinning');
            
            setTimeout(() => {
                this.classList.remove('spinning');
            }, 600);
        });
    }
    
    // Inicialización
    function initialize() {
        updateGreeting();
        initRefreshButton();
        
        if (!config.reducedMotion) {
            setTimeout(animateCounters, config.animationDelay);
        } else {
            // Si hay movimiento reducido, mostrar los valores finales directamente
            elements.counters.forEach(counter => {
                counter.textContent = counter.getAttribute('data-target') || 0;
            });
        }
        
        // Actualizar saludo cada minuto
        setInterval(updateGreeting, 60000);
    }
    
    // Ejecutar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
})(); 